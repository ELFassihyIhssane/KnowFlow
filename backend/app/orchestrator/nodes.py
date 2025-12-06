from typing import Dict
from .state import OrchestratorState
from app.agents.intent_agent import IntentAgent
from app.agents.retriever_agent import RetrieverAgent

# plus tard:
# from app.agents.summarizer_agent import SummarizerAgent
# from app.agents.concept_graph_agent import ConceptGraphAgent
# from app.agents.insight_agent import InsightAgent
# from app.agents.evaluator_agent import EvaluatorAgent


intent_agent = IntentAgent()
retriever_agent = RetrieverAgent()
# summarizer_agent = SummarizerAgent()
# concept_graph_agent = ConceptGraphAgent()
# insight_agent = InsightAgent()
# evaluator_agent = EvaluatorAgent()


def intent_node(state: OrchestratorState) -> OrchestratorState:
    result = intent_agent.analyze(state.question)
    state.intent = result.intent
    state.sub_tasks = result.sub_tasks
    return state


def retrieval_node(state: OrchestratorState) -> OrchestratorState:
    hits = retriever_agent.retrieve(query=state.question, top_k=8)
    state.retrieved_passages = hits  # FastAPI + Pydantic fera la conversion
    return state


def summarizer_node(state: OrchestratorState) -> OrchestratorState:
    # TODO: brancher ton vrai SummarizerAgent
    # Pour l’instant, version ultra simple : coller les 3 meilleurs passages
    texts = [p["text"] if isinstance(p, dict) else p.text for p in state.retrieved_passages[:3]]
    state.summary = "\n\n".join(texts)
    state.final_answer = state.summary
    return state


def concepts_node(state: OrchestratorState) -> OrchestratorState:
    # TODO: brancher ton Concept & Graph Agent
    # Pour l’instant, mock: une liste vide
    state.concepts = []
    return state


def insight_node(state: OrchestratorState) -> OrchestratorState:
    # TODO: brancher ton Insight Agent
    state.insights = "Insight (mock) basé sur les passages récupérés."
    state.final_answer = state.insights
    return state


def evaluator_node(state: OrchestratorState) -> OrchestratorState:
    # TODO: brancher ton EvaluatorAgent
    state.evaluation = {"quality": 0.8}
    return state


def router_node(state: OrchestratorState) -> Dict[str, str]:
    """
    Dit à LangGraph quelle pipeline suivre selon l'intent.
    On retourne un dict {"next": "nom_du_suivant"}.
    """
    intent = state.intent or "summary"
    if intent == "summary":
        return {"next": "summarizer"}
    elif intent == "comparison":
        return {"next": "summarizer"}   # plus tard: summary + insight
    elif intent == "concepts":
        return {"next": "concepts"}
    elif intent in ("gap", "deep_analysis"):
        return {"next": "insight"}
    else:
        return {"next": "summarizer"}
