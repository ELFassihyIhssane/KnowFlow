import json
from typing import Optional, List

from app.schemas.summarization import SummarizerResult
from app.orchestrator.state import Passage
from app.services.llm_client import call_llm
from app.services.summarization_service import build_summarizer_prompt


class SummarizerAgent:
    """
    Produit un résumé ciblé ou une comparaison basée sur les passages du Retriever.
    Sortie traçable (citations -> indices passages).
    """

    def summarize(
        self,
        question: str,
        passages: List[Passage],
        intent: Optional[str] = "summary",
        sub_tasks: Optional[List[str]] = None,
        language_hint: str = "en",
    ) -> SummarizerResult:
        if not passages:
            return SummarizerResult(
                answer="Je n'ai trouvé aucun passage pertinent pour répondre.",
                highlights=[],
                citations=[],
            )

        prompt = build_summarizer_prompt(
            question=question,
            intent=intent,
            sub_tasks=sub_tasks or [],
            passages=passages,
            language_hint=language_hint,
        )

        raw = call_llm(prompt, temperature=0.2)
        data = self._parse_json_safe(raw)

        # Normalisation légère
        data["highlights"] = self._clip_list(data.get("highlights", []), max_items=8)
        data["citations"] = self._normalize_citations(data.get("citations", []), max_index=len(passages) - 1)

        return SummarizerResult(**data)

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

        # fallback safe
        return {"answer": text.strip()[:2000], "highlights": [], "citations": []}

    def _clip_list(self, items, max_items: int):
        if not isinstance(items, list):
            return []
        out = []
        for x in items:
            s = str(x).strip()
            if s:
                out.append(s)
        return out[:max_items]

    def _normalize_citations(self, cits, max_index: int):
        if not isinstance(cits, list):
            return []
        out = []
        for x in cits:
            try:
                i = int(x)
                if 0 <= i <= max_index and i not in out:
                    out.append(i)
            except Exception:
                continue
        return out
