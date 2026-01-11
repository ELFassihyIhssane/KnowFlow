from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from enum import Enum
from datetime import datetime


class ContentType(str, Enum):
    pdf = "pdf"
    web_page = "web_page"


class CollectItem(BaseModel):
    source: str
    content_type: ContentType          
    title: str
    abstract: Optional[str] = None
    url: Optional[HttpUrl] = None      
    pdf_url: Optional[HttpUrl] = None  
    authors: List[str] = []            
    year: Optional[int] = None         
    raw_text: Optional[str] = None     
    created_at: Optional[datetime] = None
