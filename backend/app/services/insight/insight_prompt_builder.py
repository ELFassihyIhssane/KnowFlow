from __future__ import annotations

from typing import List, Dict, Any, Optional


def build_insight_prompt(
    question: str,
    summary: str,
    gaps: List[str],
    weak_concepts: List[str],
    stats: Dict[str, Any],
    passages_block: str,
    sub_tasks: Optional[List[str]] = None,   # ✅ NEW
    language: str = "en",
    intent: Optional[str] = None,
) -> str:

    mode = (intent or "insight").strip().lower()
    if mode not in ("gap", "deep_analysis", "insight"):
        mode = "insight"

    tasks = (sub_tasks or [])[:8]
    tasks_block = "\n".join(f"- {t}" for t in tasks) if tasks else "- (none)"

    if mode == "gap":
        mode_instructions = """
MODE: GAP / LIMITATIONS

Goal:
- Identify what is underexplored, weakly justified, missing evaluation, or limited in scope.
- Each point should be actionable: what is missing + why it matters + how to strengthen it.
""".strip()
    elif mode == "deep_analysis":
        mode_instructions = """
MODE: DEEP ANALYSIS

Goal:
- Provide research-grade critical analysis: evidence strength, assumptions, trade-offs, practicality,
  what results do/do not establish, and implications.
""".strip()
    else:
        mode_instructions = """
MODE: BALANCED INSIGHT

Goal:
- Provide concise expert insight: key gaps, tensions, implications, and future directions.
""".strip()

    return f"""
You are an expert scientific analyst.

{mode_instructions}

CRITICAL REQUIREMENT: SUB-TASK DRIVEN OUTPUT
- You MUST follow the provided sub_tasks IN ORDER.
- The "analysis" field MUST be a sequence of coherent paragraphs.
- Each paragraph must correspond to EXACTLY ONE supported sub_task, in the same order.
- Do NOT label or number sub_tasks in the text (no headings like "Sub-task 1").
- If a sub_task is not meaningfully supported by the retrieved passages, SKIP it silently.

NON-SUMMARY RULE (important):
- Do NOT open with "The paper introduces..." or a generic contribution summary.
- Start directly with analysis relevant to the first supported sub_task.

EVIDENCE & GROUNDING (STRICT):
- Any factual claim about the paper (methods, results, datasets, numbers, comparisons, limitations)
  MUST be supported by passages and include inline citations like [0], [2].
- You MAY extend the explanation to improve clarity (intuition, why-it-matters, implications),
  but if a statement is not explicitly supported by passages, it must either:
  (a) be purely conceptual (no new technical facts), OR
  (b) be marked as "Hypothesis:" and remain high-level.
- NEVER introduce new numbers, datasets, benchmarks, named methods, or architectural details
  unless explicitly stated in the passages.

EXPLAIN, DON'T QUOTE:
- Do not simply restate passage phrases.
- For each paragraph, include:
  1) Evidence-backed point with citation(s)
  2) Why it matters (high-level explanation; no new facts)
  3) What is underexplored / what would strengthen the claim (gap-oriented)

CONTRADICTIONS:
- Only include contradictions if supported by passages; otherwise return [].

Language: {language}

User question:
{question}

Intent:
{mode}

Sub-tasks (follow in order; skip unsupported silently):
{tasks_block}

Summary (hint only; may be incomplete):
{summary}

Heuristic gap signals (verify against passages):
{gaps}

Weakly connected concepts (optional signal):
{weak_concepts}

Statistics (coverage signal):
{stats}

Retrieved passages (evidence; cite with [index]):
{passages_block}

OUTPUT:
Return JSON ONLY (no markdown, no extra text).
Schema:
{{
  "analysis": "multi-paragraph analysis (one paragraph per supported sub_task), with citations [i] where factual",
  "gaps": ["gap statements (grounded when possible; hypotheses allowed if clearly marked)"],
  "contradictions": [],
  "future_directions": ["grounded directions; hypotheses allowed if clearly marked"]
}}

IMPORTANT OUTPUT RULES:
- If you cannot find grounded gaps, return "gaps": [] (do NOT write 'Not specified...').
- If you cannot find grounded contradictions, return "contradictions": [].
""".strip()
