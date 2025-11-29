# app/schemas/collect.py
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from enum import Enum
from datetime import datetime


class ContentType(str, Enum):
    pdf = "pdf"
    web_page = "web_page"


class CollectItem(BaseModel):
    source: str
    content_type: ContentType          # "pdf" ou "web_page"
    title: str
    abstract: Optional[str] = None
    url: Optional[HttpUrl] = None      # URL principale
    pdf_url: Optional[HttpUrl] = None  # URL du PDF si existe
    authors: List[str] = []            # ou Field(default_factory=list)
    year: Optional[int] = None         # ex: 2025
    raw_text: Optional[str] = None     # texte déjà extrait (pour pages web)
    created_at: Optional[datetime] = None
