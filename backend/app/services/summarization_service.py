from typing import List, Optional
from app.orchestrator.state import Passage


def build_passages_block(passages: List[Passage], max_passages: int = 8, max_chars_each: int = 900) -> str:

    selected = passages[:max_passages]
    blocks = []
    for i, p in enumerate(selected):
        text = (p.text or "").strip()
        if len(text) > max_chars_each:
            text = text[:max_chars_each].rstrip() + "..."
        meta = p.metadata or {}
        meta_str = (
            f"title={meta.get('title')} | year={meta.get('year')} | "
            f"source={meta.get('source')} | section={meta.get('section')}"
        )
        blocks.append(f"[{i}] {meta_str}\n{text}")
    return "\n\n".join(blocks)


def build_summarizer_prompt(
    question: str,
    intent: Optional[str],
    sub_tasks: List[str],
    passages: List[Passage],
    language_hint: str = "en",
) -> str:
    passages_block = build_passages_block(passages, max_passages=8, max_chars_each=900)
    tasks = (sub_tasks or [])[:6]
    tasks_block = "\n".join(f"{i+1}. {t}" for i, t in enumerate(tasks)) if tasks else "0. (none)"

    mode = intent or "summary"
    if mode not in ("summary", "comparison"):
        mode = "summary"
    tasks = (sub_tasks or [])[:6]
    tasks_block = "\n".join(f"{i+1}. {t}" for i, t in enumerate(tasks)) if tasks else "0. (none)"

    return f"""
You are the Summarizer Agent of a scientific orchestration system (KnowFlow).

You will receive:
- a user question
- an intent (summary or comparison)
- optional sub_tasks
- numbered retrieved passages with metadata

GOAL:
Produce an end-to-end answer that:
1) strictly follows the intent
2) addresses EVERY supported sub_task explicitly and separately (if any)
3) stays faithful to the retrieved passages for factual claims
4) explains clearly even when passages are terse

ABSOLUTE CONSTRAINTS (do not violate):
- Sub_tasks MUST be handled ONE BY ONE, in the EXACT order given.
- Each sub_task that is meaningfully supported by the retrieved passages MUST result in
  exactly ONE coherent paragraph.
- NEVER merge multiple sub_tasks into one paragraph.
- If a sub_task is NOT supported by the retrieved passages in any meaningful way,
  it MUST be SILENTLY SKIPPED (do NOT mention it explicitly).

GROUNDING RULES (very important):
- "Paper-grounded claims" MUST be supported by the passages and include inline citations like [0] [2].
- Explanatory context (definitions, intuition, clarification) MAY be included to improve clarity,
  but MUST be smoothly blended into the explanation.
- Explanatory sentences MUST NOT be presented as coming from the papers.
- Explanatory sentences MUST NOT introduce specific numbers, benchmarks, datasets,
  or named methods unless they are explicitly stated in the passages.
- Never invent citations. Never cite a passage that does not support the claim.

WRITING REQUIREMENTS (very important):
- If sub_tasks are provided, the answer MUST be structured as a sequence of coherent paragraphs.
- EACH paragraph corresponds to EXACTLY ONE supported sub_task, in the SAME order as given.
- Do NOT label, number, or explicitly mention sub_tasks in the answer.
- Do NOT use headings such as "Sub-task", "Task", or similar.
- The transition between paragraphs should feel natural and academically coherent.

CONTENT RULES PER PARAGRAPH:
- Each paragraph MUST address the intent of its corresponding sub_task.
- Paper-grounded facts MUST be integrated naturally into the explanation and cited inline (e.g., [0], [2]).
- The reader should NOT be able to distinguish which sentences come from the papers
  and which ones are explanatory, except via citations.
- Do not write citation-only sentences: explain the idea, then cite it.

STYLE:
- Write in a clear, academic, and professional tone suitable for a PhD-level reader.
- Prefer concise but complete explanations over bullet points.
- Avoid repetition, visible scaffolding, or didactic markers.

COMPARISON MODE (very important):

- If intent == "comparison", comparisons MUST be embedded naturally inside the relevant paragraphs.
- Each paragraph MUST explicitly contrast the compared approaches WITHIN the same paragraph.
- Avoid describing one approach in isolation and the other in a separate sentence or paragraph.

- Prefer direct contrastive constructions such as:
  "A does X, whereas B does Y"
  "Unlike A, B ..."
  "In contrast to A, B ..."
  "Both A and B ..., but they differ in ..."
  "A tends to ..., while B ..."

- Comparisons MUST focus ONLY on elements explicitly mentioned in the retrieved passages.
- Do NOT introduce inferred or speculative comparison axes.
- If a comparison axis is not supported by the passages, skip it silently.

IMPORTANT CLARIFICATION FOR COMPARISON MODE:
- When sub_tasks involve defining or describing individual approaches
  (e.g., "Define few-shot prompting", "Define zero-shot prompting"),
  the definition MUST be written in a contrastive manner within the SAME paragraph.
- In comparison mode, do NOT write standalone definitions for each approach.
- Instead, explicitly define each approach by contrasting it with the other
  (e.g., "Few-shot prompting does X, whereas zero-shot prompting does Y").



CITATIONS:
- Add inline citations [i] for each paper-grounded claim.
- The "citations" field MUST list ALL unique indices that appear in the answer.

OUTPUT FORMAT:
Return JSON ONLY (no markdown, no extra text).

JSON schema:
{{
  "answer": "text with [0] [2] citations where needed",
  "highlights": ["...", "..."],
  "citations": [0, 2]
}}

User question:
\"\"\"{question}\"\"\"

Intent: {mode}

Sub-tasks:
{tasks_block}

Passages:
{passages_block}
""".strip()
