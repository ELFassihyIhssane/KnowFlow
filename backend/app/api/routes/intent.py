from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.intent_agent import IntentAgent

router = APIRouter(prefix="/intent", tags=["Intent"])

agent = IntentAgent()


class IntentRequest(BaseModel):
    question: str


@router.post("/analyze")
def analyze_intent(body: IntentRequest):
    return agent.analyze(body.question)
