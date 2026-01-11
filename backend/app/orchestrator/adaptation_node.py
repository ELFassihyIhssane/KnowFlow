from __future__ import annotations

from app.orchestrator.state import OrchestratorState
from app.adaptation.service import AdaptationService
from app.adaptation.types import PipelineTuning

_adapt = AdaptationService()


def adaptation_decision_node(state: OrchestratorState) -> OrchestratorState:
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

    state.adaptation_actions = [
        {
            "name": a.name,
            "reason": a.reason,
            "patch": a.patch,
        }
        for a in decision.actions
    ]

    state.can_retry = bool(decision.should_retry)

    return state


def adaptation_router(state: OrchestratorState) -> str:
    return "end"
