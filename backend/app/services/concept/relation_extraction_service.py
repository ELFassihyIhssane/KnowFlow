import json
from typing import List, Dict

from app.services.llm_client import call_llm


REL_PROMPT = """
You are a scientific relation extraction system.

Input:
- a list of concepts
- a context text (scientific passages)

Task:
Extract directed relations between concepts, if explicitly supported by the context.

Allowed relation labels:
- uses
- improves
- depends_on
- compares_to
- outperforms
- limitation_of
- example_of
- related_to

Rules:
- Return ONLY JSON.
- Only output relations supported by context.
- No duplicates.
- Max 15 relations.

JSON format:
{
  "edges": [
    {"source": "A", "target": "B", "relation": "uses"},
    ...
  ]
}
"""


def extract_relations(concepts: List[str], context: str) -> List[Dict]:
    if not concepts or not context:
        return []

    prompt = f"""{REL_PROMPT}

Concepts:
{concepts}

Context:
\"\"\"{context[:4000]}\"\"\"
"""
    raw = call_llm(prompt, temperature=0.2)

    try:
        data = json.loads(raw)
    except Exception:
        # tentative extraction bloc JSON
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(raw[start:end+1])
            except Exception:
                return []
        else:
            return []

    edges = data.get("edges", [])
    if not isinstance(edges, list):
        return []
    # nettoyer
    cleaned = []
    seen = set()
    for e in edges:
        if not isinstance(e, dict):
            continue
        s = (e.get("source") or "").strip()
        t = (e.get("target") or "").strip()
        r = (e.get("relation") or "").strip()
        if not s or not t or not r:
            continue
        key = (s.lower(), t.lower(), r.lower())
        if key in seen:
            continue
        seen.add(key)
        cleaned.append({"source": s, "target": t, "relation": r})
    return cleaned[:15]
