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
        "insight": final_state.insight,

        # ✅ add these for manual retry UI
        "can_retry": final_state.can_retry,
        "adaptation_actions": final_state.adaptation_actions,
        "retry_count": final_state.retry_count,
        "tuning": {
            "top_k": final_state.top_k,
            "min_overlap": final_state.min_overlap,
            "temperature": final_state.temperature,
            "enable_llm_critique": final_state.enable_llm_critique,
            "enable_graph_update": final_state.enable_graph_update,
        },
    }
