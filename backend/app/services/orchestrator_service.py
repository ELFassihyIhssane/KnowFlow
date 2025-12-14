from app.orchestrator.graph_builder import build_orchestrator_graph
from app.orchestrator.state import OrchestratorState

_graph = build_orchestrator_graph()

def run_query(question: str) -> OrchestratorState:
    state = OrchestratorState(question=question)

    result = _graph.invoke(state)

    # LangGraph peut renvoyer un dict => on reconstruit l'état
    if isinstance(result, dict):
        return OrchestratorState(**result)

    return result
