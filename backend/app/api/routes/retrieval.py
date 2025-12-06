# app/api/routes/retrieval.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, List

from app.agents.retriever_agent import RetrieverAgent

router = APIRouter(prefix="/retrieval", tags=["retrieval"])


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    doc_id: Optional[int] = None  # pour filtrer par document si tu veux


@router.post("/search")
def search_documents(body: SearchRequest):
    """
    Endpoint simple pour tester le RetrieverAgent.
    """
    agent = RetrieverAgent()

    filter_by: Optional[Dict[str, str]] = None
    if body.doc_id is not None:
        filter_by = {"doc_id": body.doc_id}

    hits: List[Dict] = agent.retrieve(
        query=body.query,
        top_k=body.top_k,
        filter_by=filter_by,
    )

    return {
        "query": body.query,
        "top_k": body.top_k,
        "results": hits,
    }
