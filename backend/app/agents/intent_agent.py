import json
import re
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
   (unless it explicitly asks to extract concepts/relations/knowledge graph).
2) Use "concepts" ONLY if user explicitly asks:
   "extract concepts", "extract relations", "knowledge graph",
   "build a knowledge graph", "entities and relations", "ontology", "taxonomy".
3) Use "comparison" ONLY if user explicitly compares two things (A vs B).
4) Use "gap" if user asks for limitations, gaps, weaknesses, open problems, future work.
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

        concepts_markers_strict = [
            "extract concepts",
            "extract relations",
            "knowledge graph",
            "build a knowledge graph",
            "construct a knowledge graph",
            "entities and relations",
            "ontology",
            "taxonomy",
            "concept map",
            "knowledge map",
            "build ontology",
            "build taxonomy",
            "relations between",  
        ]

        comparison_markers = [
            "compare",
            "difference between",
            "differences between",
            "similarities between",
            "vs",
            "versus",
        ]

        gap_markers = [
            "limitations",
            "gaps",
            "weaknesses",
            "open problems",
            "future work",
            "future directions",
            "research gaps",
            "remaining challenges",
        ]

        deep_analysis_markers = [
            "critique",
            "critical analysis",
            "analyze",
            "analysis",
            "tradeoffs",
            "implications",
            "robustness",
            "failure modes",
            "why does",
            "how does it work under",
        ]

        wants_concepts = any(m in q for m in concepts_markers_strict)
        wants_gap = any(m in q for m in gap_markers)
        wants_comparison = any(m in q for m in comparison_markers)
        wants_deep = any(m in q for m in deep_analysis_markers)
        wants_definition = any(m in q for m in definition_markers)

        if wants_concepts:
            data["intent"] = "concepts"
        elif wants_gap:
            data["intent"] = "gap"
        elif wants_comparison:
            data["intent"] = "comparison"
        elif wants_deep:
            data["intent"] = "deep_analysis"
        elif wants_definition:
            data["intent"] = "summary"
        else:
            
            if data.get("intent") not in {"summary", "comparison", "concepts", "gap", "deep_analysis", "other"}:
                data["intent"] = "other"

        data["sub_tasks"] = self._normalize_sub_tasks(data.get("sub_tasks", []), data["intent"])
        return IntentResult(**data)


    # Helpers
    def _normalize_sub_tasks(self, tasks: List[str], intent: str) -> List[str]:
        """
        Cleans, truncates, limits sub-tasks, and lightly enforces verb-start.
        """
        if not isinstance(tasks, list):
            tasks = []

        out: List[str] = []
        for t in tasks:
            t = " ".join(str(t).strip().split())
            if not t:
                continue

            words = t.split(" ")
            if len(words) > 8:
                t = " ".join(words[:8])

            if not self._looks_like_imperative(t):
                prefix = self._default_task_prefix(intent)
                t = f"{prefix} {t}"
                t_words = t.split(" ")
                if len(t_words) > 8:
                    t = " ".join(t_words[:8])

            out.append(t)

        if not out:
            out = self._default_subtasks(intent)

        return out[:6]

    def _looks_like_imperative(self, t: str) -> bool:
        first = t.split(" ")[0].lower()
        common_verbs = {
            "summarize", "explain", "define", "compare", "extract", "identify",
            "list", "analyze", "evaluate", "outline", "describe", "derive", "map"
        }
        return first in common_verbs

    def _default_task_prefix(self, intent: str) -> str:
        if intent == "concepts":
            return "Extract"
        if intent == "comparison":
            return "Compare"
        if intent == "gap":
            return "Identify"
        if intent == "deep_analysis":
            return "Analyze"
        return "Explain"

    def _default_subtasks(self, intent: str) -> List[str]:
        if intent == "concepts":
            return ["Extract key concepts", "Extract key relations", "Group concepts by theme"]
        if intent == "comparison":
            return ["Identify compared items", "Compare similarities", "Compare differences"]
        if intent == "gap":
            return ["Identify limitations", "List open problems", "Suggest future directions"]
        if intent == "deep_analysis":
            return ["Analyze assumptions", "Discuss tradeoffs", "Explain implications"]
        if intent == "summary":
            return ["Summarize main idea", "Explain key points", "List applications"]
        return ["Summarize the request"]

    def _parse_json_safe(self, text: str) -> dict:
        """
        Robust JSON parsing with fallback.
        """
        cleaned = text.strip()
        cleaned = re.sub(r"^```(json)?", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

        try:
            return json.loads(cleaned)
        except Exception:
            pass

        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            snippet = cleaned[start:end + 1]
            try:
                return json.loads(snippet)
            except Exception:
                pass

        return {"intent": "summary", "sub_tasks": ["Summarize the request"]}
