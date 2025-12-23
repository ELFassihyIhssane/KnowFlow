from __future__ import annotations

import re
from typing import List, Dict, Set, Any

from app.memory.knowledge_graph import get_knowledge_graph
from app.schemas.graph import GraphEdge, GraphUpdateResult
from app.services.concept.concept_graph_service import (
    normalize_label,
    canonicalize_concept,
    find_best_match,
    choose_canonical,
)

from app.services.concept.concept_extraction_service import extract_concepts
from app.services.concept.relation_extraction_service import extract_relations

from app.services.concept.passage_gating_service import gate_passages
from app.services.concept.llm_graph_extraction_service import extract_graph_with_gemini
from app.services.concept.graph_quality_service import assess_graph_quality


def guess_node_type(label: str) -> str:
    low = (label or "").lower()

    if any(x in low for x in ["dataset", "benchmark", "corpus", "suite", "leaderboard", "webnlg", "darts"]):
        return "dataset"

    if any(x in low for x in [
        "accuracy", "precision", "recall", "f1", "auc", "bleu", "rouge", "perplexity",
        "loss", "error", "rmse", "mae", "latency", "throughput", "memory", "bandwidth",
        "reward", "return", "confidence interval", "confidence intervals"
    ]):
        return "metric"

    if any(x in low for x in [
        "classification", "segmentation", "detection", "retrieval", "generation",
        "translation", "summarization", "prediction", "clustering"
    ]) or "task" in low:
        return "task"

    if any(x in low for x in ["algorithm", "method", "approach", "framework", "architecture", "pipeline", "adapter"]):
        return "method"

    if any(x in low for x in ["model", "network", "transformer", "diffusion", "classifier", "gpt", "bert", "llama", "llm"]):
        return "model"

    if re.search(r"[a-z][A-Z]", label or "") or re.search(r"\b(v\d+|\d+\.\d+|\d+b)\b", label or "", re.IGNORECASE):
        return "model"

    return "concept"


def _tokenize(s: str) -> Set[str]:
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9\.\-\s_/]", " ", s)
    return {t for t in s.split() if len(t) > 2}


class ConceptGraphAgent:
    """
    Gemini-first KG extraction:
      1) Gate passages (higher recall + diversity)
      2) Gemini extracts {concepts, edges, evidence}
      3) Quality check aligned to question
         - OK => upsert KG and return
         - else => return debug result (NO KG pollution)
    """

    def update_from_passages(
        self,
        passages_text: str,
        question: str = "",
        section_only: bool = False,
        core_only: bool = False,
        disable_fallback: bool = True,
        debug_llm: bool = True,
    ) -> GraphUpdateResult:
        _ = section_only
        _ = core_only

        kg = get_knowledge_graph()
        question = (question or "").strip()
        passages_text = (passages_text or "").strip()

        raw_parts = [p.strip() for p in passages_text.split("\n\n") if p.strip()]

        # ✅ Increase recall and add diversity to prevent losing technique-heavy passages
        gated_parts, scores = gate_passages(
            question=question,
            passages=raw_parts,
            top_k=12,          # ✅ was 6
            min_overlap=1,
            diversify=True,
        )

        chosen_passages = gated_parts if gated_parts else raw_parts[:12]

        gem_graph = extract_graph_with_gemini(
            question=question,
            passages=chosen_passages,
            temperature=0.55,
            timeout_s=25,
        )

        ok, issues = assess_graph_quality(
            gem_graph,
            min_concepts=6,
            min_edges=2,
            require_evidence=True,
            question=question,
        )

        if debug_llm:
            try:
                print("\n================== KG LLM DEBUG ==================")
                print("[KG] question:", question)
                print("[KG] raw_parts:", len(raw_parts), "gated_parts:", len(gated_parts))
                if scores:
                    print("[KG] top gating scores:", scores[:8])
                print("[KG] chosen_passages:", len(chosen_passages))
                print("[KG] LLM concepts:", len(gem_graph.get("concepts", []) or []))
                print("[KG] LLM edges:", len(gem_graph.get("edges", []) or []))
                print("[KG] quality ok:", ok)
                print("[KG] issues:", issues)

                cons = gem_graph.get("concepts", []) or []
                eds = gem_graph.get("edges", []) or []
                if cons:
                    print("[KG] sample concepts:", [c.get("label") for c in cons[:10] if isinstance(c, dict)])
                if eds:
                    print("[KG] sample edge:", eds[0])
                print("==================================================\n")
            except Exception:
                pass

        if ok:
            return self._upsert_llm_graph(kg, gem_graph)

        # ✅ IMPORTANT FIX:
        # When quality fails and fallback is disabled, return BOTH concepts AND edges
        # so you can inspect what the LLM extracted (instead of losing relations).
        if disable_fallback:
            extracted_concepts: List[str] = []
            for c in (gem_graph.get("concepts", []) or [])[:40]:
                if isinstance(c, dict):
                    lbl = (c.get("label") or "").strip()
                    if lbl:
                        extracted_concepts.append(lbl)

            extracted_edges: List[GraphEdge] = []
            for e in (gem_graph.get("edges", []) or [])[:80]:
                if not isinstance(e, dict):
                    continue
                src = (e.get("source") or "").strip()
                tgt = (e.get("target") or "").strip()
                rel = (e.get("relation") or "").strip()
                ev = (e.get("evidence") or "").strip()
                if not src or not tgt or not rel:
                    continue

                extracted_edges.append(
                    GraphEdge(
                        source=normalize_label(src) or src,
                        target=normalize_label(tgt) or tgt,
                        relation=rel,
                        weight=0.0,  # not inserted; inspection only
                        properties={"evidence": ev} if ev else {},
                    )
                )

            # Dedup concepts
            seen = set()
            dedup_concepts: List[str] = []
            for x in extracted_concepts:
                k = x.lower()
                if k in seen:
                    continue
                seen.add(k)
                dedup_concepts.append(x)

            return GraphUpdateResult(
                nodes_added=0,
                edges_added=0,
                merged_nodes=0,
                extracted_concepts=dedup_concepts,
                extracted_edges=extracted_edges,
            )

        fallback_text = "\n\n".join(gated_parts) if gated_parts else passages_text
        return self._fallback_extract(kg, fallback_text, question)

    def _upsert_llm_graph(self, kg, gem_graph: Dict[str, Any]) -> GraphUpdateResult:
        nodes_added = 0
        merged_nodes = 0
        edges_added = 0

        extracted_concepts: List[str] = []
        extracted_edges: List[GraphEdge] = []

        existing_ids = list(kg.graph.nodes())
        norm_to_id = {
            normalize_label(kg.get_node_attrs(n).get("label", n)): n
            for n in existing_ids
        }

        concepts = gem_graph.get("concepts", []) or []
        for c in concepts[:70]:
            if not isinstance(c, dict):
                continue

            label = canonicalize_concept(str(c.get("label", "")).strip())
            if not label:
                continue

            extracted_concepts.append(label)
            norm = normalize_label(label)
            if not norm:
                continue

            if norm in norm_to_id:
                node_id = norm_to_id[norm]
                attrs = kg.get_node_attrs(node_id)
                aliases = set(attrs.get("aliases", []) or [])
                aliases.add(label)
                kg.upsert_node(
                    node_id,
                    aliases=sorted(aliases),
                    type=attrs.get("type", guess_node_type(attrs.get("label", label)))
                )
                continue

            match_norm = find_best_match(norm, list(norm_to_id.keys()), threshold=92)
            if match_norm:
                node_id = norm_to_id[match_norm]
                attrs = kg.get_node_attrs(node_id)
                old_label = attrs.get("label", node_id)

                new_label = choose_canonical(old_label, label)
                aliases = set(attrs.get("aliases", []) or [])
                aliases.update([old_label, label])

                kg.upsert_node(
                    node_id,
                    label=new_label,
                    type=guess_node_type(new_label),
                    aliases=sorted(aliases),
                )
                merged_nodes += 1
                continue

            node_id = norm
            kg.upsert_node(
                node_id,
                label=label,
                type=guess_node_type(label),
                aliases=sorted({label}),
            )
            norm_to_id[norm] = node_id
            nodes_added += 1

        seen = set()
        extracted_concepts_dedup: List[str] = []
        for x in extracted_concepts:
            k = x.lower()
            if k in seen:
                continue
            seen.add(k)
            extracted_concepts_dedup.append(x)

        edges = gem_graph.get("edges", []) or []
        dedup_edges = set()

        for e in edges[:160]:
            if not isinstance(e, dict):
                continue

            src = canonicalize_concept(str(e.get("source", "")).strip())
            tgt = canonicalize_concept(str(e.get("target", "")).strip())
            rel = str(e.get("relation", "")).strip()
            ev = str(e.get("evidence", "")).strip()

            if not src or not tgt or not rel:
                continue

            s_norm = normalize_label(src)
            t_norm = normalize_label(tgt)
            if not s_norm or not t_norm:
                continue

            key = (s_norm, t_norm, rel)
            if key in dedup_edges:
                continue
            dedup_edges.add(key)

            if not kg.has_node(s_norm):
                kg.upsert_node(s_norm, label=src, type=guess_node_type(src), aliases=[src])
                nodes_added += 1
            if not kg.has_node(t_norm):
                kg.upsert_node(t_norm, label=tgt, type=guess_node_type(tgt), aliases=[tgt])
                nodes_added += 1

            props: Dict[str, object] = {}
            if ev:
                props["evidence"] = ev

            kg.add_edge(s_norm, t_norm, relation=rel, weight=0.85, **props)
            edges_added += 1

            extracted_edges.append(
                GraphEdge(
                    source=s_norm,
                    target=t_norm,
                    relation=rel,
                    weight=0.85,
                    properties=props,
                )
            )

        kg.save()

        return GraphUpdateResult(
            nodes_added=nodes_added,
            edges_added=edges_added,
            merged_nodes=merged_nodes,
            extracted_concepts=extracted_concepts_dedup,
            extracted_edges=extracted_edges,
        )

    def _fallback_extract(self, kg, passages_text: str, question: str) -> GraphUpdateResult:
        raw_concepts = extract_concepts(passages_text, question=question, max_concepts=40)

        nodes_added = 0
        merged_nodes = 0

        existing_ids = list(kg.graph.nodes())
        norm_to_id = {
            normalize_label(kg.get_node_attrs(n).get("label", n)): n
            for n in existing_ids
        }

        kept_concepts: List[str] = []

        for c in raw_concepts:
            canon = canonicalize_concept(c)
            if not canon:
                continue

            norm = normalize_label(canon)
            if not norm:
                continue

            kept_concepts.append(canon)

            if norm in norm_to_id:
                node_id = norm_to_id[norm]
                attrs = kg.get_node_attrs(node_id)
                aliases = set(attrs.get("aliases", []) or [])
                aliases.add(c)
                aliases.add(canon)
                kg.upsert_node(node_id, aliases=sorted(aliases))
                continue

            match_norm = find_best_match(norm, list(norm_to_id.keys()), threshold=92)
            if match_norm:
                node_id = norm_to_id[match_norm]
                attrs = kg.get_node_attrs(node_id)
                old_label = attrs.get("label", node_id)

                new_label = choose_canonical(old_label, canon)
                aliases = set(attrs.get("aliases", []) or [])
                aliases.update([old_label, canon, c])

                kg.upsert_node(
                    node_id,
                    label=new_label,
                    type=guess_node_type(new_label),
                    aliases=sorted(aliases),
                )
                merged_nodes += 1
                continue

            node_id = norm
            kg.upsert_node(
                node_id,
                label=canon,
                type=guess_node_type(canon),
                aliases=sorted({c, canon}),
            )
            norm_to_id[norm] = node_id
            nodes_added += 1

        kg.save()

        return GraphUpdateResult(
            nodes_added=nodes_added,
            edges_added=0,
            merged_nodes=merged_nodes,
            extracted_concepts=kept_concepts,
            extracted_edges=[],
        )
