import json
from typing import List

from app.schemas.evaluation import EvaluationResult
from app.services.llm_client import call_llm
from app.services.evaluation.eval_faithfulness import faithfulness_score
from app.services.evaluation.eval_coverage import coverage_score
from app.services.evaluation.eval_coherence import coherence_score
from app.services.evaluation.eval_insight_depth import insight_depth_score
from app.services.evaluation.eval_llm_critique import build_critique_prompt


class EvaluatorAgent:
    """
    Hybrid Evaluator:
    - deterministic metrics
    - heuristics
    - optional LLM critique
    """

    def evaluate(
        self,
        question: str,
        answer: str,
        passages: List[str],
        use_llm: bool = True,
    ) -> EvaluationResult:

        scores = {
            "faithfulness": faithfulness_score(answer, passages),
            "coverage": coverage_score(question, answer),
            "coherence": coherence_score(answer),
            "insight_depth": insight_depth_score(answer),
        }

        global_score = round(sum(scores.values()) / len(scores), 3)

        issues, recommendations = [], []

        if use_llm:
            raw = call_llm(build_critique_prompt(question, answer), temperature=0.2)
            parsed = self._parse_json_safe(raw)
            issues = parsed.get("issues", [])
            recommendations = parsed.get("recommendations", [])

        return EvaluationResult(
            scores=scores,
            global_score=global_score,
            issues=issues,
            recommendations=recommendations,
        )

    def _parse_json_safe(self, text: str) -> dict:
        try:
            return json.loads(text)
        except Exception:
            pass
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end + 1])
            except Exception:
                pass
        return {}
