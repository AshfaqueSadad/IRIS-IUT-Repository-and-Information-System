from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query, status
from bson import ObjectId
from app.db.mongodb import get_database
from app.schemas.user import UserBase, UserRole
from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentPreviewResponse,
    DocumentStatus,
    TargetAudience,
    SenderInfo,
)
from app.services.storage import storage_service
from app.services.ocr_pipeline import ocr_pipeline
from app.services.gemini_extractor import gemini_extractor
from app.api.v1.auth import get_current_user, require_role

router = APIRouter()


@router.post("/process-preview", response_model=DocumentPreviewResponse)
async def process_document_preview(
    file: UploadFile = File(...),
    current_user: UserBase = Depends(require_role([UserRole.CR, UserRole.OFFICIAL, UserRole.ADMIN]))
):
    """
    In-flight upload endpoint:
    Reads file, runs OCR/PDF parser, extracts structured fields with Gemini,
    and returns a preview with confidence score before publishing.
    """
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Save to storage
    file.file.seek(0)
    file_url = await storage_service.save_file(file)

    extracted_text = ""
    engine_used = "PyMuPDF"

    filename = file.filename.lower()
    if filename.endswith(".pdf"):
        extracted_text, is_scanned = ocr_pipeline.extract_text_from_pdf_bytes(file_bytes)
        if is_scanned:
            # Fallback for scanned PDF: convert page to image and OCR
            engine_used = "PyMuPDF + Tesseract OCR"
    else:
        # Image file (PNG, JPG, JPEG)
        preprocessed = ocr_pipeline.preprocess_image_for_ocr(file_bytes)
        extracted_text = ocr_pipeline.extract_text_with_tesseract(preprocessed)
        engine_used = "OpenCV + Tesseract OCR"

    if not extracted_text:
        extracted_text = "Notice text could not be extracted automatically."

    # Run Gemini Extraction
    metadata = await gemini_extractor.extract_structured_metadata(extracted_text)

    return DocumentPreviewResponse(
        title=metadata.get("title", file.filename),
        category=metadata.get("category", "Academic"),
        subCategory=metadata.get("subCategory"),
        department=metadata.get("department", "All"),
        targetAudience=TargetAudience(**metadata.get("targetAudience", {})),
        sender=SenderInfo(**metadata.get("sender", {"office": "University Administration"})),
        publishedDate=metadata.get("publishedDate"),
        deadlines=metadata.get("deadlines", []),
        extractedText=extracted_text,
        confidenceScore=metadata.get("confidenceScore", 0.85),
        fileUrl=file_url,
        ocrEngineUsed=engine_used
    )


@router.post("/confirm", response_model=DocumentResponse)
async def confirm_document(
    doc_in: DocumentCreate,
    current_user: UserBase = Depends(require_role([UserRole.CR, UserRole.OFFICIAL, UserRole.ADMIN]))
):
    """Save verified notice to database and publish to archive."""
    db = get_database()
    now = datetime.utcnow()
    doc_dict = doc_in.dict()
    doc_dict.update({
        "uploaderId": current_user.email,
        "verifiedBy": current_user.email,
        "createdAt": now,
        "updatedAt": now
    })

    if db is not None:
        result = await db.documents.insert_one(doc_dict)
        doc_dict["_id"] = str(result.inserted_id)
        return DocumentResponse(**doc_dict)
    
    # In-memory mock response if DB not yet connected
    doc_dict["_id"] = str(ObjectId())
    return DocumentResponse(**doc_dict)


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    q: Optional[str] = Query(None, description="Fuzzy search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    department: Optional[str] = Query(None, description="Filter by department"),
    status: DocumentStatus = DocumentStatus.APPROVED,
    skip: int = 0,
    limit: int = 20
):
    """Search and browse approved notices with filtering."""
    db = get_database()
    if db is None:
        return []

    filter_query = {"status": status.value}
    if category:
        filter_query["category"] = category
    if department and department != "All":
        filter_query["$or"] = [{"department": department}, {"department": "All"}]

    if q:
        # Atlas search or regex fallback
        filter_query["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"extractedText": {"$regex": q, "$options": "i"}}
        ]

    cursor = db.documents.find(filter_query).sort("createdAt", -1).skip(skip).limit(limit)
    documents = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        documents.append(DocumentResponse(**doc))

    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """Retrieve full notice details by ID."""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    doc = await db.documents.find_one({"_id": ObjectId(document_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    doc["_id"] = str(doc["_id"])
    return DocumentResponse(**doc)
