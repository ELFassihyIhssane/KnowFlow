from __future__ import annotations

from typing import List, Tuple
from app.memory.knowledge_graph import get_knowledge_graph


def detect_weakly_connected_concepts(
    concepts: List[str],
    max_degree: int = 1,
    top_k: int = 10,
) -> List[str]:

    kg = get_knowledge_graph()
    if not concepts:
        return []

    weak: List[Tuple[str, int]] = []
    seen = set()

    for c in concepts:
        if not c or c in seen:
            continue
        seen.add(c)

        if not kg.graph.has_node(c):
            continue

        degree = int(kg.graph.degree(c))
        if degree <= max_degree:
            weak.append((c, degree))

    weak.sort(key=lambda x: x[1])
    return [c for c, _d in weak[:top_k]]
