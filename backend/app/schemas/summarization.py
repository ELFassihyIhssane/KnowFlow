from typing import List
from pydantic import BaseModel, Field


class SummarizerResult(BaseModel):
    """
    Sortie standard du SummarizerAgent.
    """
    answer: str = Field(..., description="Résumé final prêt pour l'utilisateur")
    highlights: List[str] = Field(default_factory=list, description="Points clés (5-8 max)")
    citations: List[int] = Field(default_factory=list, description="Indices des passages utilisés (ex: [0,2,5])")
