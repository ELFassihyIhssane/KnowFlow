from __future__ import annotations

from typing import List, Dict
import numpy as np


def compute_statistics(passages: List[str]) -> Dict[str, float]:

    lengths = [len(p.split()) for p in passages if p and p.strip()]
    if not lengths:
        return {"num_passages": 0.0}

    return {
        "avg_length": float(np.mean(lengths)),
        "max_length": float(np.max(lengths)),
        "min_length": float(np.min(lengths)),
        "num_passages": float(len(lengths)),
    }
