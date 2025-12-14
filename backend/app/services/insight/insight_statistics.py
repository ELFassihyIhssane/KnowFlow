from typing import List, Dict
import numpy as np


def compute_statistics(passages: List[str]) -> Dict[str, float]:
    lengths = [len(p.split()) for p in passages if p]

    if not lengths:
        return {}

    return {
        "avg_length": float(np.mean(lengths)),
        "max_length": float(np.max(lengths)),
        "min_length": float(np.min(lengths)),
        "num_passages": len(lengths),
    }
