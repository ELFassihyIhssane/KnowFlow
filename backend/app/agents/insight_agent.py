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
    - heuristics (regex gap detection)
    - graph reasoning (weakly connected concepts)
    - statistics (simple coverage signals)
    - LLM synthesis (grounded critical analysis)
    """

    def run(
        self,
        question: str,
        passages: List[Passage],
        summary: Optional[str],
        concepts: Optional[List[str]] = None,
        language_hint: str = "en",
        intent: Optional[str] = None,  # ✅ NEW
        sub_tasks: Optional[List[str]] = None,   # ✅ ADD THIS
    ) -> InsightResult:

        texts = [p.text for p in passages if getattr(p, "text", None)]

        gaps = detect_gaps(texts)
        stats = compute_statistics(texts)

        weak_concepts: List[str] = []
        if concepts:
            weak_concepts = detect_weakly_connected_concepts(concepts)

        # NEW: provide the agent with grounded evidence passages (numbered for citations)
        passages_block = self._build_passages_block(
            passages=passages,
            max_passages=8,
            max_chars_each=900,
        )

        prompt = build_insight_prompt(
            question=question,
            summary=summary or "",
            gaps=gaps,
            weak_concepts=weak_concepts,
            stats=stats,
            passages_block=passages_block,   # 👈 NEW ARG
            language=language_hint,
            intent=intent,  # ✅ NEW
            sub_tasks=sub_tasks,   # ✅
        )

        raw = call_llm(prompt, temperature=0.3)
        data = self._parse_json_safe(raw)

        # light normalization / safety defaults
        if not isinstance(data, dict):
            data = {}
        data.setdefault("analysis", "")
        data.setdefault("gaps", [])
        data.setdefault("contradictions", [])
        data.setdefault("future_directions", [])

        return InsightResult(**data)

    def _build_passages_block(
        self,
        passages: List[Passage],
        max_passages: int = 8,
        max_chars_each: int = 900,
    ) -> str:
        """
        Prepare numbered passages for the LLM so it can cite evidence like [0], [2].
        """
        selected = passages[:max_passages]
        blocks: List[str] = []

        for i, p in enumerate(selected):
            text = (getattr(p, "text", "") or "").strip()
            if not text:
                continue

            if len(text) > max_chars_each:
                text = text[:max_chars_each].rstrip() + "..."

            meta = getattr(p, "metadata", None) or {}
            meta_str = (
                f"title={meta.get('title')} | year={meta.get('year')} | "
                f"source={meta.get('source')} | section={meta.get('section')}"
            )

            blocks.append(f"[{i}] {meta_str}\n{text}")

        return "\n\n".join(blocks)

    def _parse_json_safe(self, text: str) -> dict:
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

        return {
            "analysis": text.strip()[:2000],
            "gaps": [],
            "contradictions": [],
            "future_directions": [],
        }
