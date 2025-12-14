from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Optional

from app.agents.summarizer_agent import SummarizerAgent
from app.orchestrator.state import Passage

router = APIRouter(prefix="/summarizer", tags=["summarizer"])
agent = SummarizerAgent()


class SummarizerRequest(BaseModel):
    question: str
    intent: Optional[str] = "summary"
    sub_tasks: List[str] = []
    passages: List[Passage]


@router.post("/run")
def run_summarizer(body: SummarizerRequest):
    return agent.summarize(
        question=body.question,
        passages=body.passages,
        intent=body.intent,
        sub_tasks=body.sub_tasks,
        language_hint="en",
    )
