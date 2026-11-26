from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class DocumentStatus(str, Enum):
    APPROVED = "APPROVED"
    PENDING_REVIEW = "PENDING_REVIEW"
    REJECTED = "REJECTED"


class SourceType(str, Enum):
    MANUAL_UPLOAD = "MANUAL_UPLOAD"
    WEB_SCRAPER = "WEB_SCRAPER"


class TargetAudience(BaseModel):
    programs: List[str] = Field(default_factory=list)
    batches: List[str] = Field(default_factory=list)
    halls: List[str] = Field(default_factory=list)


class SenderInfo(BaseModel):
    office: str
    signatory: Optional[str] = None
    rawSignatureDetected: bool = False


class DeadlineItem(BaseModel):
    title: str
    dueDate: datetime
    actionRequired: Optional[str] = None


class DocumentCreate(BaseModel):
    title: str
    category: str
    sub_category: Optional[str] = None
    department: str = "All"
    published_date: Optional[datetime] = None
    status: DocumentStatus = DocumentStatus.APPROVED
    source_type: SourceType = SourceType.MANUAL_UPLOAD
    file_url: str
    thumbnail_url: Optional[str] = None
    extracted_text: str
    confidence_score: float = 1.0
    notice_metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentPreviewResponse(BaseModel):
    title: str
    category: str
    subCategory: Optional[str] = None
    department: str = "All"
    targetAudience: TargetAudience
    sender: SenderInfo
    publishedDate: Optional[datetime] = None
    deadlines: List[DeadlineItem]
    extractedText: str
    confidenceScore: float
    fileUrl: str
    ocrEngineUsed: str


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    category: str
    sub_category: Optional[str] = None
    department: str
    published_date: Optional[datetime] = None
    status: DocumentStatus
    source_type: SourceType
    file_url: str
    thumbnail_url: Optional[str] = None
    extracted_text: str
    confidence_score: float
    notice_metadata: Dict[str, Any]
    uploader_id: Optional[UUID] = None
    verified_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
