from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.memory.models import Document
from app.cleaning.text_cleaning import clean_raw_text

router = APIRouter(prefix="/maintenance", tags=["maintenance"])


@router.post("/clean-text")
def clean_text_for_all_docs(db: Session = Depends(get_db)):
    docs = (
        db.query(Document)
        .filter(Document.raw_text.isnot(None))
        .all()
    )

    count = 0
    for doc in docs:
        doc.clean_text = clean_raw_text(doc.raw_text or "")
        count += 1

    db.commit()
    return {"updated_documents": count}