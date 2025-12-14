import json
from typing import List, Optional

from app.schemas.insight import InsightResult
from app.orchestrator.state import Passage
from app.services.llm_client import call_llm
from app.services.insight.insight_heuristics import detect_gaps
from app.services.insight.insight_statistics import compute_statistics
from app.services.insight.insight_graph_reasoning import detect_weakly_connected_concepts
from app.services.insight.insight_prompt_builder import build_insight_prompt


class InsightAgent:
    """
    Hybrid Insight Agent:
    - heuristics
    - graph reasoning
    - statistics
    - LLM synthesis
    """

    def run(
        self,
        question: str,
        passages: List[Passage],
        summary: Optional[str],
        concepts: Optional[List[str]] = None,
        language_hint: str = "en",
    ) -> InsightResult:

        texts = [p.text for p in passages if p.text]

        gaps = detect_gaps(texts)
        stats = compute_statistics(texts)

        weak_concepts = []
        if concepts:
            weak_concepts = detect_weakly_connected_concepts(concepts)

        prompt = build_insight_prompt(
            question=question,
            summary=summary or "",
            gaps=gaps,
            weak_concepts=weak_concepts,
            stats=stats,
            language=language_hint,
        )

        raw = call_llm(prompt, temperature=0.3)
        data = self._parse_json_safe(raw)

        return InsightResult(**data)

    def _parse_json_safe(self, text: str) -> dict:
        try:
            return json.loads(text)
        except Exception:
            pass

        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end + 1])
            except Exception:
                pass

        return {
            "analysis": text.strip()[:2000],
            "gaps": [],
            "contradictions": [],
            "future_directions": [],
        }
