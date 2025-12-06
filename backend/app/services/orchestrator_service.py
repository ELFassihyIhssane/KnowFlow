from app.orchestrator.graph_builder import build_orchestrator_graph
from app.orchestrator.state import OrchestratorState

_graph = build_orchestrator_graph()

def run_query(question: str) -> OrchestratorState:
    state = OrchestratorState(question=question)
    final_state = _graph.invoke(state)
    return final_state
