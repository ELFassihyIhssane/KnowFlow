# app/services/vectorization_service.py
from typing import List, Dict
from sqlalchemy.orm import Session

from app.memory.models import Document
from app.memory.embeddings import embed_texts
from app.memory.vector_store import VectorStore


def _chunk_text(
    text: str,
    max_chars: int = 800,
    overlap: int = 200,
) -> List[Dict]:
    """
    Découpe un texte en passages avec overlap.
    Retourne une liste de dicts : {"chunk_id": int, "text": str}.
    """
    chunks: List[Dict] = []
    start = 0
    idx = 0

    if not text:
        return chunks

    text = text.strip()
    if not text:
        return chunks

    while start < len(text):
        end = start + max_chars
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(
                {
                    "chunk_id": idx,
                    "text": chunk.strip(),
                }
            )
            idx += 1

        # Fenêtre glissante avec overlap
        start = end - overlap
        if start < 0:
            start = 0

    return chunks


def vectorize_all_documents(
    db: Session,
    limit: int | None = None,
) -> int:
    """
    Parcourt tous les documents
    et envoie plusieurs vecteurs par document dans Qdrant.

    Multi-Vector RAG light :
      - 1 vecteur pour le titre (section="title")
      - 1..N vecteurs pour l'abstract (section="abstract")
      - 1..N vecteurs pour le corps nettoyé (section="body") si disponible
    """
    # 👉 On ne filtre plus sur clean_text.isnot(None)
    query = db.query(Document)
    if limit:
        query = query.limit(limit)

    docs: List[Document] = query.all()

    vs = VectorStore()
    total_chunks = 0

    for doc in docs:
        # --- 1) Indexer le titre (si présent) -------------------------------
        if doc.title:
            title_texts = [doc.title.strip()]
            title_embeddings = embed_texts(title_texts)

            title_metadatas: List[Dict] = [{
                "doc_id": doc.id,
                "title": doc.title,
                "source": doc.source,
                "year": doc.year,
                "chunk_id": 0,
                "section": "title",
                "content_type": doc.content_type,
                "url": doc.url,
            }]

            vs.upsert_passages(title_texts, title_embeddings, title_metadatas)
            total_chunks += 1

        # --- 2) Indexer l'abstract (chunké si long) ------------------------
        if doc.abstract:
            abstract_chunks = _chunk_text(doc.abstract, max_chars=800, overlap=200)
            if abstract_chunks:
                abstract_texts = [c["text"] for c in abstract_chunks]
                abstract_embeddings = embed_texts(abstract_texts)

                abstract_metadatas: List[Dict] = []
                for c in abstract_chunks:
                    abstract_metadatas.append(
                        {
                            "doc_id": doc.id,
                            "title": doc.title,
                            "source": doc.source,
                            "year": doc.year,
                            "chunk_id": c["chunk_id"],
                            "section": "abstract",
                            "content_type": doc.content_type,
                            "url": doc.url,
                        }
                    )

                vs.upsert_passages(
                    abstract_texts,
                    abstract_embeddings,
                    abstract_metadatas,
                )
                total_chunks += len(abstract_chunks)

        # --- 3) Indexer le corps (clean_text chunké) -----------------------
        if doc.clean_text:
            body_chunks = _chunk_text(doc.clean_text, max_chars=800, overlap=200)
            if body_chunks:
                body_texts = [c["text"] for c in body_chunks]
                body_embeddings = embed_texts(body_texts)

                body_metadatas: List[Dict] = []
                for c in body_chunks:
                    body_metadatas.append(
                        {
                            "doc_id": doc.id,
                            "title": doc.title,
                            "source": doc.source,
                            "year": doc.year,
                            "chunk_id": c["chunk_id"],
                            "section": "body",
                            "content_type": doc.content_type,
                            "url": doc.url,
                        }
                    )

                vs.upsert_passages(body_texts, body_embeddings, body_metadatas)
                total_chunks += len(body_chunks)

    return total_chunks
