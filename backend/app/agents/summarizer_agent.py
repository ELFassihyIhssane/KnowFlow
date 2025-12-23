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

        #No passages => fallback LLM answer
        if not passages:
            fallback_prompt = f"""
You are a helpful assistant.

The user asked:
\"\"\"{question}\"\"\"

You do NOT have any retrieved evidence passages from the paper database.
- Provide a helpful general explanation based on general knowledge.
- DO NOT claim the papers said something.
- Be explicit that this is a general answer without citations.
- Keep it simple and beginner-friendly.
Return JSON only.

JSON format:
{{
  "answer": "your answer",
  "highlights": ["...", "..."],
  "citations": []
}}
""".strip()

            raw = call_llm(fallback_prompt, temperature=0.4)
            data = self._parse_json_safe(raw)

            # Add an explicit indicator in the answer
            answer = str(data.get("answer", "")).strip()
            warning = "Note: No relevant passages were retrieved, so this is a general explanation (no paper citations)."
            if warning.lower() not in answer.lower():
                answer = f"{warning}\n\n{answer}"

            data["answer"] = answer
            data["highlights"] = self._clip_list(data.get("highlights", []), max_items=8)
            data["citations"] = []
            return SummarizerResult(**data)

        # 2) Passages exist => summarize WITH evidence + simplify language
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
        max_passages_in_prompt = 8
        max_index = min(len(passages), max_passages_in_prompt) - 1
        data["citations"] = self._normalize_citations(data.get("citations", []), max_index=max_index)


        # 3) If passages exist but model returned no citations => be transparent
        if passages and not data["citations"]:
            answer = str(data.get("answer", "")).strip()
            note = "Note: The retrieved passages did not contain a direct answer; response may be partial."
            if note.lower() not in answer.lower():
                data["answer"] = f"{note}\n\n{answer}"

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