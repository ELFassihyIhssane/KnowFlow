from langgraph.graph import StateGraph, END
from .state import OrchestratorState
from . import nodes

def build_orchestrator_graph():
    graph = StateGraph(OrchestratorState)

    # 1) Nœuds
    graph.add_node("intent", nodes.intent_node)
    graph.add_node("retrieval", nodes.retrieval_node)
    graph.add_node("router", nodes.router_node)
    graph.add_node("summarizer", nodes.summarizer_node)
    graph.add_node("concepts", nodes.concepts_node)
    graph.add_node("insight", nodes.insight_node)
    graph.add_node("evaluator", nodes.evaluator_node)

    # 2) Start -> Intent -> Retrieval -> Router
    graph.set_entry_point("intent")
    graph.add_edge("intent", "retrieval")
    graph.add_edge("retrieval", "router")

    # 3) Router -> pipelines conditionnelles
    graph.add_conditional_edges(
        "router",
        lambda state: nodes.router_node(state)["next"],
        {
            "summarizer": "summarizer",
            "concepts": "concepts",
            "insight": "insight",
        },
    )

    # 4) Chaque pipeline va vers l'Evaluator, puis END
    graph.add_edge("summarizer", "evaluator")
    graph.add_edge("concepts", "evaluator")
    graph.add_edge("insight", "evaluator")
    graph.add_edge("evaluator", END)

    return graph.compile()
