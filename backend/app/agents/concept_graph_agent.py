from __future__ import annotations

from typing import List

from app.memory.knowledge_graph import get_knowledge_graph
from app.schemas.graph import GraphEdge, GraphUpdateResult
from app.services.concept.concept_graph_service import normalize_label, find_best_match, choose_canonical
from app.services.concept.concept_extraction_service import extract_concepts
from app.services.concept.relation_extraction_service import extract_relations


class ConceptGraphAgent:
    """
    Extrait concepts + relations depuis passages, puis met à jour le KG.
    """

    def update_from_passages(self, passages_text: str) -> GraphUpdateResult:
        kg = get_knowledge_graph()

        concepts = extract_concepts(passages_text, max_concepts=35)
        extracted = []

        nodes_added = 0
        merged_nodes = 0

        # index labels existants (normalisés)
        existing_ids = list(kg.graph.nodes())
        existing_norm = [normalize_label(kg.get_node_attrs(n).get("label", n)) for n in existing_ids]

        # mapping norm -> node_id (simple)
        norm_to_id = {normalize_label(kg.get_node_attrs(n).get("label", n)): n for n in existing_ids}

        for c in concepts:
            norm = normalize_label(c)
            if not norm:
                continue

            # exact match
            if norm in norm_to_id:
                extracted.append(norm_to_id[norm])
                continue

            # fuzzy match
            match_norm = find_best_match(norm, list(norm_to_id.keys()), threshold=92)
            if match_norm:
                # merge label
                node_id = norm_to_id[match_norm]
                attrs = kg.get_node_attrs(node_id)
                old_label = attrs.get("label", node_id)
                new_label = choose_canonical(old_label, c)
                kg.upsert_node(node_id, label=new_label, type="concept")
                merged_nodes += 1
                extracted.append(node_id)
                continue

            # create new node id = normalized string
            node_id = norm
            kg.upsert_node(node_id, label=c, type="concept")
            norm_to_id[norm] = node_id
            nodes_added += 1
            extracted.append(node_id)

        # relations (LLM) à partir du contexte
        edges_raw = extract_relations(concepts=concepts, context=passages_text)

        edges_added = 0
        extracted_edges: List[GraphEdge] = []

        for e in edges_raw:
            s = normalize_label(e["source"])
            t = normalize_label(e["target"])
            rel = e["relation"]

            if not s or not t:
                continue

            # assurer noeuds
            if not kg.has_node(s):
                kg.upsert_node(s, label=e["source"], type="concept")
                nodes_added += 1
            if not kg.has_node(t):
                kg.upsert_node(t, label=e["target"], type="concept")
                nodes_added += 1

            kg.add_edge(s, t, relation=rel, weight=1.0)
            edges_added += 1
            extracted_edges.append(GraphEdge(source=s, target=t, relation=rel, weight=1.0, properties={}))

        kg.save()

        return GraphUpdateResult(
            nodes_added=nodes_added,
            edges_added=edges_added,
            merged_nodes=merged_nodes,
            extracted_concepts=concepts,
            extracted_edges=extracted_edges,
        )
