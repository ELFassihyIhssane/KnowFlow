# app/api/routes/vectorization.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.vectorization_service import vectorize_all_documents

router = APIRouter(prefix="/vectorization", tags=["vectorization"])


@router.post("/vectorize-all")
def vectorize_all_docs_endpoint(
    limit: int | None = None,
    db: Session = Depends(get_db),
):
    total_chunks = vectorize_all_documents(db, limit=limit)
    return {
        "status": "ok",
        "indexed_passages": total_chunks,
    }
