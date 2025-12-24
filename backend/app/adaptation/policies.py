# backend/app/adaptation/policies.py
from __future__ import annotations

from typing import Optional

from app.adaptation.types import AdaptationAction, AdaptationDecision, PipelineTuning
from app.schemas.evaluation import EvaluationResult


def apply_policies(
    *,
    intent: str,
    tuning: PipelineTuning,
    evaluation: Optional[EvaluationResult],
    latency_ms: Optional[float] = None,
) -> AdaptationDecision:
    """
    Rules-first adaptation (manual retry friendly):
    - if weak coverage => recommend expanding retrieval (top_k)
    - if weak faithfulness => recommend reducing temperature + enforce critique
    - if low coherence => recommend critique
    - latency guard => recommend disabling critique for speed
    """
    decision = AdaptationDecision(tuning=tuning, actions=[], should_retry=False)

    if evaluation is None:
        return decision

    # ✅ IMPORTANT: your EvaluationResult stores metrics inside `evaluation.scores`
    scores = getattr(evaluation, "scores", {}) or {}
    cov = scores.get("coverage")
    fai = scores.get("faithfulness")
    coh = scores.get("coherence")
    global_score = getattr(evaluation, "global_score", None)

    # --- Latency guard (soft) ---
    if latency_ms is not None and latency_ms > 8000:
        if tuning.enable_llm_critique:
            decision.actions.append(
                AdaptationAction(
                    name="disable_llm_critique",
                    reason="High latency detected; disabling critique for speed.",
                    patch={"enable_llm_critique": False},
                )
            )

    # --- Coverage low => more/better retrieval ---
    if cov is not None and cov < 0.55:
        new_top_k = min(12, tuning.top_k + 4)
        if new_top_k != tuning.top_k:
            decision.actions.append(
                AdaptationAction(
                    name="increase_top_k",
                    reason=f"Coverage low ({cov:.2f}); expanding retrieval context.",
                    patch={"top_k": new_top_k},
                )
            )
        decision.should_retry = True
        decision.retry_with = PipelineTuning(**{**tuning.__dict__, "top_k": new_top_k})
        decision.retry_with.notes.append("Retry due to low coverage")

    # Optional fallback: if global score is quite low, also suggest retry
    if global_score is not None and global_score < 0.55:
        decision.should_retry = True

    # --- Faithfulness low => less hallucination risk ---
    if fai is not None and fai < 0.60:
        new_temp = max(0.05, tuning.temperature - 0.10)
        decision.actions.append(
            AdaptationAction(
                name="reduce_temperature",
                reason=f"Faithfulness low ({fai:.2f}); reducing temperature.",
                patch={"temperature": new_temp},
            )
        )
        # encourage critique if available
        decision.actions.append(
            AdaptationAction(
                name="enable_llm_critique",
                reason="Faithfulness low; enabling critique to enforce grounding.",
                patch={"enable_llm_critique": True},
            )
        )

    # --- Coherence low => critique or re-summarize hint ---
    if coh is not None and coh < 0.55:
        decision.actions.append(
            AdaptationAction(
                name="enable_llm_critique",
                reason=f"Coherence low ({coh:.2f}); enabling critique for structure.",
                patch={"enable_llm_critique": True},
            )
        )

    # Intent-based soft rules
    if intent in {"comparison", "gap_analysis"} and tuning.top_k < 8:
        decision.actions.append(
            AdaptationAction(
                name="intent_boost_top_k",
                reason=f"Intent={intent}; boosting retrieval depth.",
                patch={"top_k": 8},
            )
        )

    return decision
