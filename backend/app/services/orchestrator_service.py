import time

from app.orchestrator.graph_builder import build_orchestrator_graph
from app.orchestrator.state import OrchestratorState

from app.adaptation.service import AdaptationService
from app.adaptation.types import PipelineTuning

from app.observability.logging import get_logger
from app.observability.tracing import Tracer

log = get_logger("knowflow.query")
tracer = Tracer()
adapt = AdaptationService()

_graph = build_orchestrator_graph()


def run_query(state_or_question) -> OrchestratorState:
    if isinstance(state_or_question, OrchestratorState):
        state = state_or_question
    else:
        state = OrchestratorState(question=str(state_or_question))

    t0 = time.perf_counter()

    with tracer.trace(name="run_query", metadata={"question": state.question}) as tr:
        result = _graph.invoke(state)

        out = OrchestratorState(**result) if isinstance(result, dict) else result

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        log.info("run_query_done", latency_ms=round(elapsed_ms, 2))
        return out
