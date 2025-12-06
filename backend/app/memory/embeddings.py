# app/memory/embeddings.py
from functools import lru_cache
from typing import List
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2" 
VECTOR_SIZE = 384  


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Charge le modèle d'embeddings une seule fois (singleton).
    """
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    model.max_seq_length = 512
    return model


def embed_text(text: str) -> List[float]:
    """
    Embedding d'un seul texte (pour les requêtes).
    """
    model = get_embedding_model()
    vec = model.encode(text, normalize_embeddings=True)
    return vec.tolist()


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Embedding d'une liste de textes (pour l'indexation).
    """
    model = get_embedding_model()
    vectors = model.encode(texts, normalize_embeddings=True, batch_size=16)
    return [v.tolist() for v in vectors]
