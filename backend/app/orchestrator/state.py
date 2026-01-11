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

    insights: Optional[str] = None

    insight: Optional[Dict[str, Any]] = None

    evaluation: Optional[EvaluationResult] = None
    final_answer: Optional[str] = None

    top_k: int = 8
    min_overlap: int = 1
    temperature: float = 0.2
    enable_llm_critique: bool = True
    enable_graph_update: bool = True

    retry_count: int = 0
    can_retry: bool = False  
    adaptation_actions: List[Dict[str, Any]] = Field(default_factory=list)
