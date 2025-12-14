import json
from typing import List

from app.schemas.intent import IntentResult
from app.services.llm_client import call_llm


SYSTEM_PROMPT = """
You are the Intent & Decomposition Agent of KnowFlow (scientific knowledge platform).

Choose exactly ONE primary intent:
- summary: explain/define/overview + applications/uses
- comparison: compare A vs B (differences/similarities)
- concepts: extract concepts/entities/relations OR build/extend a knowledge graph
- gap: limitations / missing pieces / open problems / future work
- deep_analysis: critical analysis, tradeoffs, implications, deep reasoning
- other: anything else

Routing rules (important):
1) If the question contains "what is", "define", "explain", "overview",
   "introduction", "applications", "use cases"
   => intent MUST be "summary"
   (unless it explicitly asks to extract concepts/relations).
2) Use "concepts" ONLY if user explicitly asks:
   "extract concepts", "extract relations", "knowledge graph",
   "entities", "graph", "relations between", "taxonomy".
3) Use "comparison" ONLY if user explicitly compares two things (A vs B).
4) Use "gap" if user asks for limitations, gaps, weaknesses, future directions.
5) Use "deep_analysis" for deep critical analysis beyond summary.

Output rules:
- Output ONLY valid JSON.
- No explanations.
- No markdown.
- No extra text.
- Provide 3 to 6 sub_tasks maximum.
- Each sub_task must be very short (max 8 words).
- Each sub_task must start with a verb.

JSON format:
{
  "intent": "<one_of_allowed_intents>",
  "sub_tasks": ["...", "..."]
}
"""


class IntentAgent:
    """
    Classifies the user intent and decomposes the query
    into short atomic sub-tasks for KnowFlow orchestration.
    """

    def analyze(self, question: str) -> IntentResult:
        prompt = f"""{SYSTEM_PROMPT}

User question:
\"\"\"{question}\"\"\"
"""
        raw = call_llm(prompt)
        data = self._parse_json_safe(raw)

        # -------------------------
        # HARD HEURISTIC OVERRIDES
        # -------------------------
        q = question.lower()

        definition_markers = [
            "what is",
            "define",
            "explain",
            "overview",
            "introduction",
            "applications",
            "use cases",
        ]

        graph_markers = [
            "extract concepts",
            "extract relations",
            "knowledge graph",
            "entities",
            "relations between",
            "taxonomy",
            "graph",
        ]

        comparison_markers = ["compare", "difference between", "vs", "versus"]

        gap_markers = ["limitations", "gaps", "weaknesses", "open problems", "future work"]

        # Force SUMMARY for definition-style questions
        if any(m in q for m in definition_markers) and not any(m in q for m in graph_markers):
            data["intent"] = "summary"

        # Force CONCEPTS if explicit graph request
        if any(m in q for m in graph_markers):
            data["intent"] = "concepts"

        # Force COMPARISON
        if any(m in q for m in comparison_markers):
            data["intent"] = "comparison"

        # Force GAP
        if any(m in q for m in gap_markers):
            data["intent"] = "gap"

        data["sub_tasks"] = self._normalize_sub_tasks(data.get("sub_tasks", []))
        return IntentResult(**data)

    # -------------------------
    # Helpers
    # -------------------------
    def _normalize_sub_tasks(self, tasks: List[str]) -> List[str]:
        """
        Cleans, truncates, and limits sub-tasks.
        """
        if not isinstance(tasks, list):
            return []

        out = []
        for t in tasks:
            t = " ".join(str(t).strip().split())
            words = t.split(" ")
            if len(words) > 8:
                t = " ".join(words[:8])
            if t:
                out.append(t)
        return out[:6]

    def _parse_json_safe(self, text: str) -> dict:
        """
        Robust JSON parsing with fallback.
        """
        try:
            return json.loads(text)
        except Exception:
            pass

        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except Exception:
                pass

        # Ultimate safe fallback
        return {
            "intent": "summary",
            "sub_tasks": ["Summarize the request"],
        }
