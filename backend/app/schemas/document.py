from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


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
    subCategory: Optional[str] = None
    department: str = "All"
    targetAudience: TargetAudience = Field(default_factory=TargetAudience)
    sender: SenderInfo
    publishedDate: Optional[datetime] = None
    deadlines: List[DeadlineItem] = Field(default_factory=list)
    extractedText: str
    confidenceScore: float = 1.0
    status: DocumentStatus = DocumentStatus.APPROVED
    sourceType: SourceType = SourceType.MANUAL_UPLOAD
    fileUrl: str
    thumbnailUrl: Optional[str] = None


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


class DocumentResponse(DocumentCreate):
    id: str = Field(..., alias="_id")
    createdAt: datetime
    updatedAt: datetime
    uploaderId: Optional[str] = None
    verifiedBy: Optional[str] = None
