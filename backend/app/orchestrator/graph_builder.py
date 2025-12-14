from langgraph.graph import StateGraph, END
from app.orchestrator.state import OrchestratorState
from app.orchestrator import nodes


def build_orchestrator_graph():
    graph = StateGraph(OrchestratorState)

    # ---------- Nodes ----------
    graph.add_node("intent", nodes.intent_node)
    graph.add_node("retrieval", nodes.retrieval_node)
    graph.add_node("summarizer", nodes.summarizer_node)
    graph.add_node("concepts", nodes.concepts_node)
    graph.add_node("insight", nodes.insight_node)
    graph.add_node("evaluator", nodes.evaluator_node)

    # ✅ Nouveau node "vide" (pas de logique), juste pour brancher du routing
    graph.add_node("post_summary_router", lambda state: state)

    # ---------- Start ----------
    graph.set_entry_point("intent")
    graph.add_edge("intent", "retrieval")

    # ---------- Routing après retrieval ----------
    graph.add_conditional_edges(
        "retrieval",
        nodes.route_selector,
        {
            "summarizer": "summarizer",
            "concepts": "concepts",
            "insight": "insight",
        },
    )

    # ---------- Après summarizer : décider si on passe par Insight ----------
    graph.add_edge("summarizer", "post_summary_router")
    graph.add_conditional_edges(
        "post_summary_router",
        nodes.post_summary_selector,
        {
            "insight": "insight",
            "evaluator": "evaluator",
        },
    )

    # ---------- Fin pipeline ----------
    graph.add_edge("concepts", "evaluator")
    graph.add_edge("insight", "evaluator")
    graph.add_edge("evaluator", END)

    return graph.compile()
