import json
import re
from typing import List, Dict, Set, Optional

from app.services.llm_client import call_llm
from app.services.concept.concept_graph_service import canonicalize_concept


ALLOWED_RELATIONS = {
    "uses",
    "improves",
    "depends_on",
    "compares_to",
    "outperforms",
    "limitation_of",
    "example_of",
    "distinguishes",
    "maximizes",
    "minimizes",
    "part_of",
    "evaluated_on",
}

NOISE_TOKENS = {
    "foundation", "grant", "funded", "support",
    "university", "institute", "laboratory",
    "acknowledgement", "acknowledgment", "et al",
}


def _looks_like_noise_concept(s: str) -> bool:
    if not s:
        return True
    low = s.lower().strip()
    if re.search(r"\[\s*\d+(?:\s*,\s*\d+)*\s*\]", s):
        return True
    if re.search(r"\b(algorithm|table|figure)\s+\d+\b", low):
        return True
    if sum(ch.isdigit() for ch in s) >= 3:
        return True
    if any(tok in low for tok in NOISE_TOKENS):
        return True
    return False


def _tokenize(s: str) -> Set[str]:
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9\.\-\s_/]", " ", s)
    return {t for t in s.split() if len(t) > 2}


# -------------------------
# 1) Heuristic relations (fast, reliable)
# -------------------------
def _extract_relations_heuristic(concepts: List[str], context: str) -> List[Dict]:
    """
    Universel : quelques patterns simples, haute précision.
    """
    edges: List[Dict] = []
    ctx = context

    # build a quick lookup for concept presence
    lowered = {c.lower(): c for c in concepts}

    def add_edge(a: str, b: str, rel: str, ev: str):
        edges.append({"source": a, "target": b, "relation": rel, "evidence": ev[:200]})

    # Pattern: "X is part of Y"
    for a in concepts:
        for b in concepts:
            if a == b:
                continue
            pat = re.compile(rf"\b{re.escape(a)}\b.*?\bis part of\b.*?\b{re.escape(b)}\b", re.IGNORECASE)
            m = pat.search(ctx)
            if m:
                add_edge(a, b, "part_of", m.group(0))
                if len(edges) >= 6:
                    return edges

    # Pattern: "X depends on Y" / "requires"
    for a in concepts:
        for b in concepts:
            if a == b:
                continue
            pat = re.compile(rf"\b{re.escape(a)}\b.*?\b(depends on|requires|relies on)\b.*?\b{re.escape(b)}\b", re.IGNORECASE)
            m = pat.search(ctx)
            if m:
                add_edge(a, b, "depends_on", m.group(0))
                if len(edges) >= 10:
                    return edges

    return edges


# -------------------------
# 2) LLM completer (question-aware + evidence)
# -------------------------
REL_PROMPT = """
You are a scientific relation extraction system.

You will receive:
- User question (what the user cares about)
- A list of canonical concepts
- Context text (scientific passages)
- Optional: existing heuristic edges

Task:
Extract directed relations BETWEEN the provided concepts, ONLY if explicitly supported by the context.
Prioritize relations that help answer the user question.

Allowed relation labels:
- uses
- improves
- depends_on
- compares_to
- outperforms
- limitation_of
- example_of
- distinguishes
- maximizes
- minimizes
- part_of
- evaluated_on

Rules:
- Return ONLY valid JSON.
- No guessing. If not supported, output nothing.
- Use ONLY the provided concepts as source/target.
- Provide a short evidence span from the context for each edge (<= 25 words).
- No duplicates.
- Max 15 edges.

JSON format:
{
  "edges": [
    {"source": "A", "target": "B", "relation": "uses", "evidence": "..."}
  ]
}
""".strip()


def extract_relations(concepts: List[str], context: str, question: str = "") -> List[Dict]:
    if not concepts or not context:
        return []

    # Canonicalize + filter concepts
    canonical_concepts: List[str] = []
    seen: Set[str] = set()

    for c in concepts:
        c = (c or "").strip()
        if not c or _looks_like_noise_concept(c):
            continue

        canon = canonicalize_concept(c)
        if not canon or _looks_like_noise_concept(canon):
            continue

        key = canon.lower()
        if key in seen:
            continue
        seen.add(key)
        canonical_concepts.append(canon)

    if len(canonical_concepts) < 2:
        return []

    allowed_nodes = {c.lower() for c in canonical_concepts}

    # --- Heuristic first (high precision)
    heuristic_edges = _extract_relations_heuristic(canonical_concepts, context)

    # --- Question focus terms (generic)
    q_toks = _tokenize(question)
    focus = sorted(list(q_toks))[:25]  # cap

    prompt = f"""{REL_PROMPT}

User question:
{question}

Focus terms from question (for relevance):
{focus}

Concepts:
{canonical_concepts}

Existing heuristic edges:
{heuristic_edges}

Context:
\"\"\"{context[:4000]}\"\"\"
"""

    raw = call_llm(prompt, temperature=0.2)
    data = _parse_json_safe(raw)
    edges = data.get("edges", [])
    if not isinstance(edges, list):
        edges = []

    # --- Clean + validate
    cleaned: List[Dict] = []
    dedup = set()

    for e in (heuristic_edges + edges):
        if not isinstance(e, dict):
            continue

        s = canonicalize_concept((e.get("source") or "").strip())
        t = canonicalize_concept((e.get("target") or "").strip())
        r = (e.get("relation") or "").strip()
        ev = (e.get("evidence") or "").strip()

        if not s or not t or not r:
            continue
        if r not in ALLOWED_RELATIONS:
            continue
        if _looks_like_noise_concept(s) or _looks_like_noise_concept(t):
            continue

        # Must connect known canonical concepts
        if s.lower() not in allowed_nodes or t.lower() not in allowed_nodes:
            continue

        # Evidence requirement (keeps KG meaningful)
        if len(ev.split()) < 3:
            continue

        # Extra sanity: evidence should mention at least one endpoint
        ev_low = ev.lower()
        if s.lower() not in ev_low and t.lower() not in ev_low:
            continue

        key = (s.lower(), t.lower(), r.lower())
        if key in dedup:
            continue
        dedup.add(key)

        cleaned.append({"source": s, "target": t, "relation": r, "evidence": ev})

        if len(cleaned) >= 15:
            break

    return cleaned


def _parse_json_safe(raw: str) -> Dict:
    if not raw:
        return {}
    text = raw.strip()
    text = re.sub(r"^```(json)?", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text).strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = text[start:end + 1]
        try:
            return json.loads(snippet)
        except Exception:
            return {}

    return {}
