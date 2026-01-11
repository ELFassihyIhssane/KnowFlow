from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PipelineTuning:
    
    top_k: int = 6
    min_overlap: int = 1  
    rerank: bool = False

    model: str = "default"
    temperature: float = 0.2
    max_tokens: int = 800

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
