from __future__ import annotations

from typing import List


def build_critique_prompt(question: str, answer: str, passages: List[str]) -> str:
    # keep passages short to reduce token cost
    max_passages = 6
    trimmed = []
    for i, p in enumerate((passages or [])[:max_passages]):
        p = (p or "").strip()
        if len(p) > 700:
            p = p[:700].rstrip() + "..."
        trimmed.append(f"[{i}] {p}")

    passages_block = "\n\n".join(trimmed) if trimmed else "(none)"

    return f"""
You are a critical scientific reviewer.

Your job:
- Identify concrete issues in the answer relative to the question and evidence passages.
- Do NOT rewrite the answer.
- Be concise and actionable.
- If you suspect an unsupported claim, say so.

Question:
{question}

Answer:
{answer}

Evidence passages (for checking support):
{passages_block}

Return JSON ONLY:
{{
  "issues": ["..."],
  "recommendations": ["..."]
}}
""".strip()
