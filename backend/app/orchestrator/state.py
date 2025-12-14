from typing import List, Dict, Optional
from pydantic import BaseModel

from app.schemas.evaluation import EvaluationResult  


class Passage(BaseModel):
    text: str
    score: float
    metadata: Dict[str, object]


class OrchestratorState(BaseModel):
    question: str

    intent: Optional[str] = None
    sub_tasks: List[str] = []

    retrieved_passages: List[Passage] = []

    summary: Optional[str] = None
    concepts: List[Dict[str, str]] = []
    insights: Optional[str] = None

    evaluation: Optional[EvaluationResult] = None

    final_answer: Optional[str] = None
