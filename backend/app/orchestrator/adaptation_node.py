from __future__ import annotations

from app.orchestrator.state import OrchestratorState
from app.adaptation.service import AdaptationService
from app.adaptation.types import PipelineTuning

_adapt = AdaptationService()


def adaptation_decision_node(state: OrchestratorState) -> OrchestratorState:
    """
    Computes adaptation recommendations.
    DOES NOT trigger retry.
    Only stores recommendations in state for UI / manual retry.
    """
    if state.evaluation is None:
        state.adaptation_actions = []
        state.can_retry = False
        return state

    tuning = PipelineTuning(
        top_k=state.top_k,
        min_overlap=state.min_overlap,
        temperature=state.temperature,
        enable_llm_critique=state.enable_llm_critique,
        enable_graph_update=state.enable_graph_update,
    )

    decision = _adapt.decide(
        intent=state.intent or "summary",
        current_tuning=tuning,
        evaluation=state.evaluation,
        latency_ms=None,
    )

    # Store actions (NO auto-apply)
    state.adaptation_actions = [
        {
            "name": a.name,
            "reason": a.reason,
            "patch": a.patch,
        }
        for a in decision.actions
    ]

    # Let UI know retry is possible (but not executed)
    state.can_retry = bool(decision.should_retry)

    return state


def adaptation_router(state: OrchestratorState) -> str:
    """
    Manual retry only → always end the graph.
    """
    return "end"
