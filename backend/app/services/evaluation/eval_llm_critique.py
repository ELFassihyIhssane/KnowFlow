def build_critique_prompt(question: str, answer: str) -> str:
    return f"""
You are a critical scientific reviewer.

Evaluate the answer quality.
Do NOT rewrite the answer.
Return short issues and recommendations.

Question:
{question}

Answer:
{answer}

Return JSON ONLY:
{{
  "issues": [...],
  "recommendations": [...]
}}
"""
