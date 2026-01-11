# app/agents/retriever_agent.py
from typing import List, Dict, Optional

from app.memory.embeddings import embed_text
from app.memory.vector_store import VectorStore


class RetrieverAgent:

    def __init__(self, collection_name: str | None = None):
        self.vs = VectorStore(collection_name=collection_name) if collection_name else VectorStore()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter_by: Optional[Dict[str, str]] = None,
    ) -> List[Dict]:
        
        q_vec = embed_text(query)
        hits = self.vs.search(
            query_embedding=q_vec,
            top_k=top_k,
            filter_by=filter_by,
        )
        return hits
