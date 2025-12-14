from typing import List, Optional
from app.orchestrator.state import Passage


def build_passages_block(passages: List[Passage], max_passages: int = 8, max_chars_each: int = 900) -> str:
    """
    Prépare un bloc de passages numérotés pour le LLM.
    Numérotation = citations traçables.
    """
    selected = passages[:max_passages]
    blocks = []
    for i, p in enumerate(selected):
        text = (p.text or "").strip()
        if len(text) > max_chars_each:
            text = text[:max_chars_each].rstrip() + "..."
        meta = p.metadata or {}
        meta_str = f"title={meta.get('title')} | year={meta.get('year')} | source={meta.get('source')} | section={meta.get('section')}"
        blocks.append(f"[{i}] {meta_str}\n{text}")
    return "\n\n".join(blocks)


def build_summarizer_prompt(
    question: str,
    intent: Optional[str],
    sub_tasks: List[str],
    passages: List[Passage],
    language_hint: str = "en",
) -> str:
    """
    Construit le prompt du Summarizer.
    """
    passages_block = build_passages_block(passages)

    tasks_block = "\n".join(f"- {t}" for t in (sub_tasks or [])[:6]) if sub_tasks else "- (none)"

    mode = intent or "summary"
    if mode not in ("summary", "comparison"):
        mode = "summary"  # Le summarizer est surtout summary/comparison

    return f"""
You are the Summarizer Agent of a scientific orchestration system (KnowFlow).

You will receive:
- a user question
- an intent (summary or comparison)
- optional sub_tasks
- numbered passages with metadata

Your job:
- Produce a concise, faithful answer based ONLY on the passages.
- If intent == "comparison", structure the answer as a comparison (A vs B).
- Return JSON ONLY.

Hard rules:
- Use ONLY provided passages. If insufficient, say what is missing.
- Add citations as passage indices like [0], [1] in the answer.
- citations field must list the used indices.
- highlights: 5 to 8 bullets max.
- Language: {language_hint}.

JSON format:
{{
  "answer": "text with [0] [2] citations",
  "highlights": ["...", "..."],
  "citations": [0,2]
}}

User question:
\"\"\"{question}\"\"\"

Intent: {mode}

Sub-tasks:
{tasks_block}

Passages:
{passages_block}
""".strip()
