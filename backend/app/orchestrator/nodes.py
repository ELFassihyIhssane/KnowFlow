from typing import List, Optional, Dict, Any

from app.orchestrator.state import OrchestratorState, Passage
from app.agents.intent_agent import IntentAgent
from app.agents.retriever_agent import RetrieverAgent
from app.agents.summarizer_agent import SummarizerAgent
from app.agents.insight_agent import InsightAgent
from app.agents.concept_graph_agent import ConceptGraphAgent
from app.agents.evaluator_agent import EvaluatorAgent
from app.schemas.evaluation import EvaluationResult

from app.services.concept.concept_graph_service import normalize_label, canonicalize_concept
from app.memory.knowledge_graph import get_knowledge_graph
from app.services.concept.passage_gating_service import gate_passages

from app.observability.logging import get_logger
log = get_logger("knowflow.retrieval")

# Agents instanciés une seule fois
intent_agent = IntentAgent()
_retriever_agent: Optional[RetrieverAgent] = None  # lazy
summarizer_agent = SummarizerAgent()
concept_agent = ConceptGraphAgent()
insight_agent = InsightAgent()
evaluator_agent = EvaluatorAgent()

insight: Optional[Dict[str, Any]] = None


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
    log.info("retrieval_params", top_k=state.top_k, retry_count=state.retry_count, temperature=state.temperature, enable_llm_critique=state.enable_llm_critique,)
    retriever = _get_retriever()  # Qdrant appelé seulement ici
    hits = retriever.retrieve(query=state.question, top_k=state.top_k)

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
    return "evaluator"


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
    passages = [p for p in (state.retrieved_passages or []) if getattr(p, "text", None)]
    passages = passages[:12]

    if not passages:
        state.concepts = []
        state.final_answer = "No passages were retrieved, so no concepts could be extracted."
        return state

    raw_parts = []
    for p in passages:
        txt = (p.text or "").strip()
        if not txt:
            continue
        if len(txt) > 1500:
            txt = txt[:1500].rstrip() + "..."
        raw_parts.append(txt)

    question = (state.question or "").strip()

    # ✅ gate passages (avoid mixed-doc context)
    gated_parts, _scores = gate_passages(
        question=question,
        passages=raw_parts,
        top_k=min(12, max(4, state.top_k)),  # cohérent avec retrieval
        min_overlap=state.min_overlap,
    )

    ctx_parts = gated_parts if gated_parts else raw_parts[:6]
    ctx = "\n\n".join(ctx_parts).strip()

    if not ctx:
        state.concepts = []
        state.final_answer = "Retrieved passages were empty after cleaning, so no concepts could be extracted."
        return state

    # Gemini-first happens inside the agent
    result = concept_agent.update_from_passages(
        passages_text=ctx,
        question=question,
        section_only=False,
        core_only=False,
    )

    concepts_raw = (result.extracted_concepts or [])[:25]
    edges = (result.extracted_edges or [])[:30]

    kg = get_knowledge_graph()

    structured = []
    seen_ids = set()

    for label in concepts_raw:
        canon = canonicalize_concept(label)
        cid = normalize_label(canon)
        if not cid or cid in seen_ids:
            continue

        if not kg.has_node(cid):
            kg.upsert_node(cid, label=canon, type="concept", aliases=[label, canon])

        seen_ids.add(cid)
        structured.append({"id": cid, "label": kg.get_node_attrs(cid).get("label", canon)})

    state.concepts = structured

    id_to_label = {}
    for c in structured:
        attrs = kg.get_node_attrs(c["id"])
        id_to_label[c["id"]] = attrs.get("label", c["label"])

    lines = []
    lines.append("Extracted concepts:")
    for c in structured[:12]:
        lines.append(f"• {c['label']}")

    if edges:
        by_rel = {}
        for e in edges:
            by_rel.setdefault(e.relation, []).append(e)
        
        lines.append("")
        lines.append("Detected relations:")
        lines.append("")
        for rel, rel_edges in list(by_rel.items())[:5]:
            lines.append(f"{rel}:")
            for e in rel_edges[:5]:
                src_label = id_to_label.get(e.source) or kg.get_node_attrs(e.source).get("label", e.source)
                tgt_label = id_to_label.get(e.target) or kg.get_node_attrs(e.target).get("label", e.target)

                ev = ""
                if getattr(e, "properties", None) and isinstance(e.properties, dict):
                    ev = (e.properties.get("evidence") or "").strip()

                if ev:
                    if len(ev) > 180:
                        ev = ev[:180].rstrip() + "..."
                    lines.append(f"• {src_label} → {tgt_label}  \n  evidence:{ev}")
                else:
                    lines.append(f"• {src_label} → {tgt_label}")

    lines.append("\nNote: Extracted from retrieved passages, normalized and aligned to your question.")
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
        intent=state.intent,  # ✅ NEW
        sub_tasks=state.sub_tasks,   # ✅ ADD THIS
    )

    state.insight = res.model_dump() if hasattr(res, "model_dump") else res.dict()
    state.insights = res.analysis
    return state


# ---------- EVALUATOR NODE ----------
def evaluator_node(state: OrchestratorState) -> OrchestratorState:
    # Build final_answer once (do not overwrite if already set)
    if not state.final_answer:
        # ✅ If intent is insight-driven, prefer InsightAgent output
        if state.intent in ("gap", "deep_analysis"):
            if state.insight and isinstance(state.insight, dict) and state.insight.get("analysis"):
                state.final_answer = state.insight["analysis"]
            elif state.insights:
                state.final_answer = state.insights
            elif state.summary:
                state.final_answer = state.summary
            else:
                state.final_answer = ""
        else:
            # ✅ Normal mode: prefer summary
            if state.summary:
                state.final_answer = state.summary
            elif state.insights:
                state.final_answer = state.insights
            elif state.insight and isinstance(state.insight, dict) and state.insight.get("analysis"):
                # fallback safety
                state.final_answer = state.insight["analysis"]
            else:
                state.final_answer = ""

    passages_text = [p.text for p in state.retrieved_passages]

    result = evaluator_agent.evaluate(
        question=state.question,
        answer=state.final_answer,
        passages=passages_text,
        sub_tasks=state.sub_tasks,   # ✅ NEW
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
