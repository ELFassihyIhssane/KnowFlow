from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.memory.models import Document
from app.cleaning.text_cleaning import clean_raw_text


def clean_all_documents():
    """
    Parcourt tous les documents avec raw_text non nul
    et met à jour cleaned_text.
    """
    db: Session = SessionLocal()
    try:
        docs = (
            db.query(Document)
            .filter(Document.raw_text.isnot(None))
            .all()
        )

        for doc in docs:
            cleaned = clean_raw_text(doc.raw_text or "")
            doc.clean_text = cleaned

        db.commit()
    finally:
        db.close()