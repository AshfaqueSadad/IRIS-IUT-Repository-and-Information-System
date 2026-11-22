from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, desc

from app.db.database import get_db
from app.models.document import NoticeDocument
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
from app.api.v1.auth import require_role

router = APIRouter()


@router.post("/process-preview", response_model=DocumentPreviewResponse)
async def process_document_preview(
    file: UploadFile = File(...),
    current_user: UserBase = Depends(require_role([UserRole.CR, UserRole.OFFICIAL, UserRole.ADMIN]))
):
    """
    In-flight upload endpoint:
    Reads file, runs OCR/PDF parser, extracts structured fields with Gemini,
    and returns a preview with confidence score before committing to PostgreSQL.
    """
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Save to storage (S3 / R2 or local fallback)
    file.file.seek(0)
    file_url = await storage_service.save_file(file)

    extracted_text = ""
    engine_used = "PyMuPDF"

    filename = file.filename.lower()
    if filename.endswith(".pdf"):
        extracted_text, is_scanned = ocr_pipeline.extract_text_from_pdf_bytes(file_bytes)
        if is_scanned:
            engine_used = "PyMuPDF + Tesseract OCR"
    else:
        preprocessed = ocr_pipeline.preprocess_image_for_ocr(file_bytes)
        extracted_text = ocr_pipeline.extract_text_with_tesseract(preprocessed)
        engine_used = "OpenCV + Tesseract OCR"

    if not extracted_text:
        extracted_text = "Notice text could not be extracted automatically."

    # Run Gemini Structured Extraction
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
    current_user: UserBase = Depends(require_role([UserRole.CR, UserRole.OFFICIAL, UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """Save verified notice to PostgreSQL database and publish to archive."""
    db_doc = NoticeDocument(
        title=doc_in.title,
        category=doc_in.category,
        sub_category=doc_in.sub_category,
        department=doc_in.department,
        published_date=doc_in.published_date,
        status=doc_in.status.value,
        source_type=doc_in.source_type.value,
        file_url=doc_in.file_url,
        thumbnail_url=doc_in.thumbnail_url,
        extracted_text=doc_in.extracted_text,
        confidence_score=doc_in.confidence_score,
        notice_metadata=doc_in.notice_metadata,
        uploader_id=current_user.email,
        verified_by=current_user.email
    )

    db.add(db_doc)
    await db.commit()
    await db.refresh(db_doc)

    return DocumentResponse.model_validate(db_doc)


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    q: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    department: Optional[str] = Query(None, description="Filter by department"),
    status: DocumentStatus = DocumentStatus.APPROVED,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Search and browse approved notices in PostgreSQL with filtering."""
    query = select(NoticeDocument).where(NoticeDocument.status == status.value)

    if category:
        query = query.where(NoticeDocument.category == category)
    if department and department != "All":
        query = query.where(
            or_(NoticeDocument.department == department, NoticeDocument.department == "All")
        )

    if q:
        query = query.where(
            or_(
                NoticeDocument.title.ilike(f"%{q}%"),
                NoticeDocument.extracted_text.ilike(f"%{q}%")
            )
        )

    query = query.order_by(desc(NoticeDocument.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    docs = result.scalars().all()

    return [DocumentResponse.model_validate(doc) for doc in docs]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve full notice details by UUID."""
    result = await db.execute(select(NoticeDocument).where(NoticeDocument.id == document_id))
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    return DocumentResponse.model_validate(doc)
