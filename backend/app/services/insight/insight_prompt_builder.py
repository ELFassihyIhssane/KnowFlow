def build_insight_prompt(
    question: str,
    summary: str,
    gaps: list,
    weak_concepts: list,
    stats: dict,
    language: str = "fr",
) -> str:
    return f"""
You are an expert scientific analyst.

Your role:
- Synthesize insights based on provided signals
- DO NOT invent facts
- DO NOT summarize papers

Signals provided:
- Summary
- Detected gaps
- Weakly connected concepts
- Simple statistics

Produce a clear expert analysis.

Language: {language}

Question:
{question}

Summary:
{summary}

Detected gaps:
{gaps}

Weak concepts:
{weak_concepts}

Statistics:
{stats}

Return ONLY JSON:
{{
  "analysis": "...",
  "gaps": [...],
  "contradictions": [...],
  "future_directions": [...]
}}
"""
