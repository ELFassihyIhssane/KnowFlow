from __future__ import annotations

import json
import os
from typing import Dict, List, Optional, Tuple

import networkx as nx


class KnowledgeGraphStore:
    """
    Stockage local du Knowledge Graph (NetworkX).
    Persistance simple en JSON (fichier).
    """

    def __init__(self, path: str = "data/knowledge_graph.json"):
        self.path = path
        self.graph = nx.MultiDiGraph()
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self._load_if_exists()

    def _load_if_exists(self) -> None:
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._from_dict(data)
        except Exception:
            # si fichier cassé, on repart clean
            self.graph = nx.MultiDiGraph()

    def save(self) -> None:
        data = self._to_dict()
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _to_dict(self) -> Dict:
        nodes = []
        for node_id, attrs in self.graph.nodes(data=True):
            nodes.append({"id": node_id, **attrs})

        edges = []
        for u, v, k, attrs in self.graph.edges(keys=True, data=True):
            edges.append({"source": u, "target": v, "key": str(k), **attrs})

        return {"nodes": nodes, "edges": edges}

    def _from_dict(self, data: Dict) -> None:
        self.graph = nx.MultiDiGraph()

        for n in data.get("nodes", []):
            node_id = n.get("id")
            attrs = {k: v for k, v in n.items() if k != "id"}
            if node_id:
                self.graph.add_node(node_id, **attrs)

        for e in data.get("edges", []):
            u = e.get("source")
            v = e.get("target")
            attrs = {k: v for k, v in e.items() if k not in ("source", "target", "key")}
            if u and v:
                self.graph.add_edge(u, v, **attrs)

    # --- API Graph ---
    def upsert_node(self, node_id: str, **attrs) -> None:
        if self.graph.has_node(node_id):
            self.graph.nodes[node_id].update(attrs)
        else:
            self.graph.add_node(node_id, **attrs)

    def add_edge(self, source: str, target: str, **attrs) -> None:
        self.graph.add_edge(source, target, **attrs)

    def has_node(self, node_id: str) -> bool:
        return self.graph.has_node(node_id)

    def get_node_attrs(self, node_id: str) -> Dict:
        return dict(self.graph.nodes[node_id]) if self.graph.has_node(node_id) else {}

    def neighbors_subgraph(self, seed_nodes: List[str], hops: int = 1) -> nx.MultiDiGraph:
        """
        Retourne un sous-graphe autour de seed_nodes.
        """
        if not seed_nodes:
            return nx.MultiDiGraph()

        visited = set(seed_nodes)
        frontier = set(seed_nodes)

        for _ in range(hops):
            nxt = set()
            for n in frontier:
                if not self.graph.has_node(n):
                    continue
                nxt.update(self.graph.successors(n))
                nxt.update(self.graph.predecessors(n))
            nxt = {x for x in nxt if x not in visited}
            visited.update(nxt)
            frontier = nxt

        return self.graph.subgraph(visited).copy()


# singleton simple
_kg_singleton: Optional[KnowledgeGraphStore] = None


def get_knowledge_graph() -> KnowledgeGraphStore:
    global _kg_singleton
    if _kg_singleton is None:
        _kg_singleton = KnowledgeGraphStore()
    return _kg_singleton
