from typing import List, Optional
from app.orchestrator.state import OrchestratorState, Passage
from app.agents.intent_agent import IntentAgent
from app.agents.retriever_agent import RetrieverAgent
from app.agents.summarizer_agent import SummarizerAgent
from app.agents.insight_agent import InsightAgent
from app.agents.concept_graph_agent import ConceptGraphAgent
from app.agents.evaluator_agent import EvaluatorAgent
from app.schemas.evaluation import EvaluationResult

# Agents instanciés une seule fois
intent_agent = IntentAgent()
_retriever_agent: Optional[RetrieverAgent] = None  # lazy
summarizer_agent = SummarizerAgent()
concept_agent = ConceptGraphAgent()
insight_agent = InsightAgent()
evaluator_agent = EvaluatorAgent()


def _get_retriever() -> RetrieverAgent:
    global _retriever_agent
    if _retriever_agent is None:
        _retriever_agent = RetrieverAgent()
    return _retriever_agent

# ---------- INTENT NODE ----------
def intent_node(state: OrchestratorState) -> OrchestratorState:
    result = intent_agent.analyze(state.question)
    state.intent = result.intent
    state.sub_tasks = result.sub_tasks
    return state


# ---------- RETRIEVAL NODE ----------
def retrieval_node(state: OrchestratorState) -> OrchestratorState:
    retriever = _get_retriever()  # Qdrant appelé seulement ici
    hits = retriever.retrieve(query=state.question, top_k=8)

    state.retrieved_passages = [
        Passage(
            text=h["text"],
            score=h["score"],
            metadata=h.get("metadata", {}),
        )
        for h in hits
    ]
    return state

def post_summary_selector(state: OrchestratorState) -> str:
    return "insight" if state.intent == "comparison" else "evaluator"

# ---------- SUMMARIZER NODE ----------
def summarizer_node(state: OrchestratorState) -> OrchestratorState:
    result = summarizer_agent.summarize(
        question=state.question,
        passages=state.retrieved_passages,
        intent=state.intent,
        sub_tasks=state.sub_tasks,
        language_hint="en",
    )
    state.summary = result.answer
    # Optionnel: stocker highlights/citations dans evaluation ou un champ dédié plus tard
    return state


# ---------- CONCEPT GRAPH NODE ----------
def concepts_node(state: OrchestratorState) -> OrchestratorState:
    ctx = "\n\n".join([p.text for p in state.retrieved_passages[:8] if p.text])
    result = concept_agent.update_from_passages(ctx)

    concepts = result.extracted_concepts[:20]
    edges = result.extracted_edges[:20]

    state.concepts = [{"label": c} for c in concepts]

    #réponse finale texte (pour /api/query)
    lines = []
    lines.append("Concepts extraits :")
    for c in concepts[:12]:
        lines.append(f"- {c}")

    if edges:
        lines.append("\nRelations détectées :")
        for e in edges[:12]:
            lines.append(f"- {e.source} --{e.relation}--> {e.target}")

    state.final_answer = "\n".join(lines)
    return state




# ---------- INSIGHT NODE ----------
def insight_node(state: OrchestratorState) -> OrchestratorState:
    res = insight_agent.run(
        question=state.question,
        passages=state.retrieved_passages,
        summary=state.summary,
        concepts=[c["label"] for c in state.concepts] if state.concepts else [],
        language_hint="en",
    )
    state.insights = res.analysis
    return state



# ---------- EVALUATOR NODE ----------
def evaluator_node(state: OrchestratorState) -> OrchestratorState:
    # Ne pas écraser si déjà produit (concepts_node)
    if not state.final_answer:
        if state.summary:
            state.final_answer = state.summary
        elif state.insights:
            state.final_answer = state.insights
        else:
            state.final_answer = ""

    passages_text = [p.text for p in state.retrieved_passages]

    result = evaluator_agent.evaluate(
        question=state.question,
        answer=state.final_answer,
        passages=passages_text,
    )

    state.evaluation = EvaluationResult(
        scores=result.scores,
        global_score=result.global_score,
        issues=result.issues,
        recommendations=result.recommendations,
    )
    return state


# ---------- ROUTE SELECTOR (PAS UN NODE) ----------
def route_selector(state: OrchestratorState) -> str:
    """
    Décide quelle pipeline activer selon l'intent.
    """
    intent = state.intent or "summary"

    if intent in ("summary", "comparison"):
        return "summarizer"
    if intent == "concepts":
        return "concepts"
    if intent in ("gap", "deep_analysis"):
        return "insight"

    return "summarizer"
