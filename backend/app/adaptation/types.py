# backend/app/adaptation/types.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PipelineTuning:
    # retrieval
    top_k: int = 6
    min_overlap: int = 1  # if you gate passages
    rerank: bool = False

    # llm/model routing
    model: str = "default"
    temperature: float = 0.2
    max_tokens: int = 800

    # behavior
    enable_graph_update: bool = True
    enable_llm_critique: bool = True

    notes: List[str] = field(default_factory=list)


@dataclass
class AdaptationAction:
    name: str
    reason: str
    patch: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AdaptationDecision:
    tuning: PipelineTuning
    actions: List[AdaptationAction] = field(default_factory=list)
    should_retry: bool = False
    retry_with: Optional[PipelineTuning] = None
