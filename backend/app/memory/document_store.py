from sqlalchemy.orm import Session
from .models import Document
from ..schemas.collect import CollectItem

def save_metadata(db: Session, item: CollectItem) -> int:
    # 1) check if doc already exists by URL
    if item.url:
        existing = db.query(Document).filter(Document.url == str(item.url)).first()
        if existing:
            return existing.id

    # 2) otherwise create a new one
    doc = Document(
        source=item.source,
        content_type=item.content_type.value,
        title=item.title,
        abstract=item.abstract,
        url=str(item.url) if item.url else None,
        pdf_url=str(item.pdf_url) if item.pdf_url else None,
        authors=item.authors or [],
        year=item.year,
        raw_text=item.raw_text,
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc.id
