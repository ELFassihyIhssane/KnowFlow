from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from ..core.db import Base


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        UniqueConstraint("url", name="uq_documents_url"),
    )

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, nullable=True)   # used for dedup
    source = Column(String, index=True)
    content_type = Column(String, index=True)
    title = Column(String, index=True)
    abstract = Column(Text, nullable=True)
    pdf_url = Column(String, nullable=True)
    authors = Column(JSONB, nullable=True)             # list of strings
    year = Column(Integer, nullable=True)
    raw_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
