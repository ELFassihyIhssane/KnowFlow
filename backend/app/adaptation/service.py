from __future__ import annotations

from typing import Optional

from app.adaptation.policies import apply_policies
from app.adaptation.types import AdaptationDecision, PipelineTuning
from app.schemas.evaluation import EvaluationResult


class AdaptationService:
    def decide(
        self,
        *,
        intent: str,
        current_tuning: PipelineTuning,
        evaluation: Optional[EvaluationResult],
        latency_ms: Optional[float] = None,
    ) -> AdaptationDecision:
        return apply_policies(
            intent=intent,
            tuning=current_tuning,
            evaluation=evaluation,
            latency_ms=latency_ms,
        )
