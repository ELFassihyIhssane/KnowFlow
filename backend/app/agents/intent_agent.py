from typing import List, Dict
from pydantic import BaseModel

# Plus tard tu mettras un vrai LLM (Ollama, HF, etc.)
# Pour l’instant logique simple + tu peux améliorer après.
class IntentResult(BaseModel):
    intent: str
    sub_tasks: List[str]

class IntentAgent:
    """
    Comprend la nature de la question :
      - summary
      - comparison
      - concepts
      - gap
      - deep_analysis
    Et éventuellement des sous-tâches.
    """

    def analyze(self, question: str) -> IntentResult:
        q = question.lower()

        if "compare" in q or "difference" in q:
            intent = "comparison"
        elif "limit" in q or "gap" in q or "future work" in q:
            intent = "gap"
        elif "concept" in q or "explain" in q or "definition" in q:
            intent = "concepts"
        elif "analyze" in q or "analysis" in q or "insight" in q:
            intent = "deep_analysis"
        else:
            intent = "summary"

        # Version simple : 1 seule sous-tâche = la question elle-même
        return IntentResult(intent=intent, sub_tasks=[question])
