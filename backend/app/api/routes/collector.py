# app/api/routes/collector.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...schemas.collect import CollectItem
from ...core.db import get_db
from ...memory.document_store import save_metadata

router = APIRouter()


@router.post("/collector/ingest")
async def ingest_article(item: CollectItem, db: Session = Depends(get_db)):
    """
    Reçoit un document depuis n8n (PDF ou page web),
    l'enregistre dans PostgreSQL et renvoie son id.
    """
    doc_id = save_metadata(db, item)

    return {
        "status": "metadata_saved",
        "doc_id": doc_id,
        "title": item.title,
        "source": item.source,
        "content_type": item.content_type,
    }
