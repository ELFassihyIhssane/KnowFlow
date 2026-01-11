from typing import List, Dict, Any, Optional
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)

from app.config import settings
from app.memory.embeddings import VECTOR_SIZE


DEFAULT_COLLECTION = "knowflow_passages"


class VectorStore:
    def __init__(self, collection_name: str = DEFAULT_COLLECTION):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )
        self.collection_name = collection_name
        self._ensure_collection()

    def _ensure_collection(self):
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )

    def reset_collection(self):
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )

    def upsert_passages(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ):

        if metadatas is None:
            metadatas = [{} for _ in texts]

        points = []
        for text, emb, meta in zip(texts, embeddings, metadatas):
            payload = {
                "text": text,
                **meta,
            }
            points.append(
                PointStruct(
                    id=str(uuid4()),
                    vector=emb,
                    payload=payload,
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_by: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:

        qdrant_filter = None
        if filter_by:
            conditions = []
            for field, value in filter_by.items():
                conditions.append(
                    FieldCondition(
                        key=field,
                        match=MatchValue(value=value),
                    )
                )
            qdrant_filter = Filter(must=conditions)

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            query_filter=qdrant_filter,
            limit=top_k,
        )

        hits = response.points  

        results: List[Dict[str, Any]] = []
        for h in hits:
            payload = h.payload or {}
            results.append(
                {
                    "id": h.id,
                    "score": h.score,
                    "text": payload.get("text", ""),
                    "metadata": {k: v for k, v in payload.items() if k != "text"},
                }
            )
        return results