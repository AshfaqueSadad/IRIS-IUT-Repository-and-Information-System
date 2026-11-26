import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.database import Base


class NoticeDocument(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    sub_category = Column(String(100), nullable=True)
    department = Column(String(100), nullable=False, default="All", index=True)
    published_date = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False, default="APPROVED", index=True)
    source_type = Column(String(50), nullable=False, default="MANUAL_UPLOAD")
    file_url = Column(String(1000), nullable=False)
    thumbnail_url = Column(String(1000), nullable=True)
    extracted_text = Column(Text, nullable=False)
    confidence_score = Column(Float, default=1.0)

    # PostgreSQL native JSONB column for dynamic AI extraction & structured metadata
    # Stores: targetAudience, sender, deadlines, raw OCR features
    notice_metadata = Column(JSONB, nullable=False, default=dict)

    uploader_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    uploader = relationship("User", foreign_keys=[uploader_id])
    verifier = relationship("User", foreign_keys=[verified_by])

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # GIN index on notice_metadata JSONB column for high-speed sub-field queries
    __table_args__ = (
        Index("ix_documents_metadata_gin", notice_metadata, postgresql_using="gin"),
    )
