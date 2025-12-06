from typing import List, Dict, Optional
from pydantic import BaseModel

class Passage(BaseModel):
    text: str
    score: float
    metadata: Dict[str, object]

class OrchestratorState(BaseModel):
    question: str

    intent: Optional[str] = None           # "summary", "comparison", "concepts", "gap", "deep_analysis"
    sub_tasks: List[str] = []              # sous-questions

    retrieved_passages: List[Passage] = [] # passages du Retriever
    summary: Optional[str] = None          # sortie Summarizer
    concepts: List[Dict[str, str]] = []    # sorties Concept & Graph
    insights: Optional[str] = None         # sortie Insight Agent

    evaluation: Optional[Dict[str, float]] = None  # scores Evaluator
    final_answer: Optional[str] = None     # réponse finale que tu renverras à l’UI
