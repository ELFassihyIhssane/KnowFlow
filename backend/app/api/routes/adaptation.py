from fastapi import APIRouter
from app.services.orchestrator_service import run_query
from app.orchestrator.state import OrchestratorState

router = APIRouter(prefix="/query", tags=["query"])


@router.post("/retry")
def retry_query(payload: dict):
    state = OrchestratorState(
        question=payload["question"],
        retry_count=payload.get("retry_count", 0) + 1,
    )

    for action in payload.get("adaptation_actions", []):
        patch = action.get("patch", {}) or {}
        for k, v in patch.items():
            if hasattr(state, k):
                setattr(state, k, v)

    final_state = run_query(state)

    return {
        "question": state.question,
        "intent": final_state.intent,
        "sub_tasks": final_state.sub_tasks,
        "answer": final_state.final_answer,
        "passages": final_state.retrieved_passages,
        "evaluation": final_state.evaluation,
        "insight": final_state.insight,
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
