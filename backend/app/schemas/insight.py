from typing import List
from pydantic import BaseModel, Field


class InsightResult(BaseModel):

    analysis: str = Field(..., description="Analyse critique synthétisée")
    gaps: List[str] = Field(default_factory=list, description="Manques / limites identifiés")
    contradictions: List[str] = Field(default_factory=list, description="Contradictions détectées")
    future_directions: List[str] = Field(default_factory=list, description="Pistes futures proposées")
