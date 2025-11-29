from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...core.db import get_db
from ...services.text_extraction_service import process_all_documents

router = APIRouter()


@router.post("/extract-text")
def extract_text_endpoint(db: Session = Depends(get_db)):
    processed = process_all_documents(db)
    return {
        "status": "ok",
        "processed_documents": processed
    }
