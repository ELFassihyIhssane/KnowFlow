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
    Rules-first adaptation:
    - if weak coverage => expand retrieval
    - if weak faithfulness => reduce creativity + ask for stricter citation usage
    - if low coherence => enable critique or re-summarize
    - latency guard => avoid heavy steps
    """
    decision = AdaptationDecision(tuning=tuning, actions=[], should_retry=False)

    if evaluation is None:
        # no evaluation => keep defaults
        return decision

    cov = getattr(evaluation, "coverage", None)
    fai = getattr(evaluation, "faithfulness", None)
    coh = getattr(evaluation, "coherence", None)

    # --- Latency guard (soft)
    if latency_ms is not None and latency_ms > 8000:
        # avoid heavy critique and graph updates when slow
        if tuning.enable_llm_critique:
            tuning.enable_llm_critique = False
            decision.actions.append(
                AdaptationAction(
                    name="disable_llm_critique",
                    reason="High latency detected; disabling critique for speed.",
                    patch={"enable_llm_critique": False},
                )
            )

    # --- Coverage low => more/better retrieval
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

        # suggest retry (only once) with expanded retrieval
        decision.should_retry = True
        decision.retry_with = PipelineTuning(**{**tuning.__dict__, "top_k": new_top_k})
        decision.retry_with.notes.append("Retry due to low coverage")

    # --- Faithfulness low => less hallucination risk
    if fai is not None and fai < 0.60:
        new_temp = max(0.05, tuning.temperature - 0.10)
        if new_temp != tuning.temperature:
            decision.actions.append(
                AdaptationAction(
                    name="reduce_temperature",
                    reason=f"Faithfulness low ({fai:.2f}); reducing temperature.",
                    patch={"temperature": new_temp},
                )
            )
        tuning.temperature = new_temp

        # encourage critique if available
        if not tuning.enable_llm_critique:
            tuning.enable_llm_critique = True
            decision.actions.append(
                AdaptationAction(
                    name="enable_llm_critique",
                    reason="Faithfulness low; enabling critique to enforce grounding.",
                    patch={"enable_llm_critique": True},
                )
            )

    # --- Coherence low => critique or re-summarize hint
    if coh is not None and coh < 0.55:
        if not tuning.enable_llm_critique:
            tuning.enable_llm_critique = True
            decision.actions.append(
                AdaptationAction(
                    name="enable_llm_critique",
                    reason=f"Coherence low ({coh:.2f}); enabling critique for structure.",
                    patch={"enable_llm_critique": True},
                )
            )

    # Intent-based soft rules
    if intent in {"comparison", "gap_analysis"}:
        # these need more context generally
        if tuning.top_k < 8:
            tuning.top_k = 8
            decision.actions.append(
                AdaptationAction(
                    name="intent_boost_top_k",
                    reason=f"Intent={intent}; boosting retrieval depth.",
                    patch={"top_k": 8},
                )
            )

    return decision
