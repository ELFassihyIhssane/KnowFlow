from typing import List
from app.memory.knowledge_graph import get_knowledge_graph


def detect_weakly_connected_concepts(concepts: List[str]) -> List[str]:
    kg = get_knowledge_graph()
    weak = []

    for c in concepts:
        if not kg.graph.has_node(c):
            continue
        degree = kg.graph.degree(c)
        if degree <= 1:
            weak.append(c)

    return weak
