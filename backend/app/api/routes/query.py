from fastapi import APIRouter
from pydantic import BaseModel
from app.services.orchestrator_service import run_query

router = APIRouter(prefix="/query", tags=["query"])

class QueryRequest(BaseModel):
    question: str

@router.post("")
def query_endpoint(body: QueryRequest):
    final_state = run_query(body.question)

    return {
        "question": body.question,
        "intent": final_state.intent,
        "sub_tasks": final_state.sub_tasks,
        "answer": final_state.final_answer,
        "passages": final_state.retrieved_passages,
        "evaluation": final_state.evaluation,
    }
