from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

from app.schemas.evaluation import EvaluationResult


class Passage(BaseModel):
    text: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class OrchestratorState(BaseModel):
    question: str

    intent: Optional[str] = None
    sub_tasks: List[str] = Field(default_factory=list)

    retrieved_passages: List[Passage] = Field(default_factory=list)

    summary: Optional[str] = None
    concepts: List[Dict[str, str]] = Field(default_factory=list)

    # Backward-compatible: old UI expects a single text field
    insights: Optional[str] = None

    # ✅ New: full structured InsightResult (analysis/gaps/contradictions/future_directions)
    insight: Optional[Dict[str, Any]] = None

    evaluation: Optional[EvaluationResult] = None
    final_answer: Optional[str] = None
