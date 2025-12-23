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


def run_query(question: str) -> OrchestratorState:
    state = OrchestratorState(question=question)

    t0 = time.perf_counter()

    with tracer.trace(name="run_query", metadata={"question": question}) as tr:
        try:
            result = _graph.invoke(state)

            # LangGraph peut renvoyer un dict => on reconstruit l'état
            if isinstance(result, dict):
                out = OrchestratorState(**result)
            else:
                out = result

            elapsed_ms = (time.perf_counter() - t0) * 1000.0

            # --- Adaptation (NON-bloquante): on observe et on log, sans relancer le pipeline ---
            try:
                if out.evaluation is not None:
                    # Tuning par défaut (tu peux remplacer par tes valeurs réelles si tu en as)
                    tuning = PipelineTuning()

                    decision = adapt.decide(
                        intent=out.intent or "summary",
                        current_tuning=tuning,
                        evaluation=out.evaluation,
                        latency_ms=elapsed_ms,
                    )

                    log.info(
                        "adaptation_decision",
                        should_retry=decision.should_retry,
                        actions=[a.name for a in decision.actions],
                        reasons=[a.reason for a in decision.actions],
                        patch=[a.patch for a in decision.actions],
                    )
                else:
                    log.info("adaptation_skipped", reason="No evaluation in state")
            except Exception as adapt_err:
                # jamais bloquant : si adaptation fail, on continue
                log.warning("adaptation_error", error=str(adapt_err))

            log.info("run_query_done", latency_ms=round(elapsed_ms, 2))
            return out

        except Exception as e:
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            log.error("run_query_error", latency_ms=round(elapsed_ms, 2), error=str(e))
            raise
