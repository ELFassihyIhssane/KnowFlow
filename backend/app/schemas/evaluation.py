from typing import Dict, List
from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    scores: Dict[str, float] = Field(
        ..., description="Scores par dimension (0-1)"
    )
    global_score: float = Field(
        ..., description="Score global agrégé"
    )
    issues: List[str] = Field(
        default_factory=list, description="Problèmes détectés"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Actions recommandées"
    )
