from typing import List, Literal
from pydantic import BaseModel, Field


IntentType = Literal[
    "summary",
    "comparison",
    "concepts",
    "gap",
    "deep_analysis",
    "other"
]


class IntentResult(BaseModel):
    """
    Résultat standardisé de l'Intent & Decomposition Agent
    utilisé par l'Orchestrator.
    """
    intent: IntentType = Field(
        ...,
        description="Type principal de la requête utilisateur"
    )
    sub_tasks: List[str] = Field(
        default_factory=list,
        description="Sous-tâches atomiques à exécuter par les agents"
    )
