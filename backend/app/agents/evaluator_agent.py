import json
from typing import List, Optional

from app.schemas.evaluation import EvaluationResult
from app.services.llm_client import call_llm
from app.services.evaluation.eval_faithfulness import faithfulness_score
from app.services.evaluation.eval_coverage import coverage_score
from app.services.evaluation.eval_coherence import coherence_score
from app.services.evaluation.eval_insight_depth import insight_depth_score
from app.services.evaluation.eval_llm_critique import build_critique_prompt


class EvaluatorAgent:
    """
    Hybrid Evaluator (robust MVP):
    - deterministic proxies (faithfulness/coverage/coherence/insight)
    - optional LLM critique grounded by evidence passages
    """

    def evaluate(
        self,
        question: str,
        answer: str,
        passages: List[str],
        sub_tasks: Optional[List[str]] = None,
        use_llm: bool = True,
    ) -> EvaluationResult:

        scores = {
            "faithfulness": faithfulness_score(answer, passages),
            "coverage": coverage_score(question, answer, sub_tasks=sub_tasks),
            "coherence": coherence_score(answer),
            "insight_depth": insight_depth_score(answer),
        }

        # Weighted global score (more sensible than uniform average)
        weights = {
            "faithfulness": 0.40,
            "coverage": 0.25,
            "coherence": 0.20,
            "insight_depth": 0.15,
        }
        global_score = round(
            sum(scores[k] * weights.get(k, 0.0) for k in scores.keys()) / sum(weights.values()),
            3
        )

        issues, recommendations = [], []

        if use_llm:
            raw = call_llm(build_critique_prompt(question, answer, passages), temperature=0.2)
            parsed = self._parse_json_safe(raw)
            issues = parsed.get("issues", []) if isinstance(parsed.get("issues", []), list) else []
            recommendations = parsed.get("recommendations", []) if isinstance(parsed.get("recommendations", []), list) else []

        return EvaluationResult(
            scores=scores,
            global_score=global_score,
            issues=[str(x).strip() for x in issues if str(x).strip()],
            recommendations=[str(x).strip() for x in recommendations if str(x).strip()],
        )

    def _parse_json_safe(self, text: str) -> dict:
        try:
            return json.loads(text)
        except Exception:
            pass
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except Exception:
                pass
        return {}
