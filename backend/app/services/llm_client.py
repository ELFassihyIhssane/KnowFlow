import time
import logging
import google.generativeai as genai
from app.config import settings

logger = logging.getLogger("knowflow.llm")


class LLMError(Exception):
    pass


_model = None  # cache pour éviter de recréer le modèle à chaque requête


def init_gemini():
    if not settings.GEMINI_API_KEY:
        raise LLMError("GEMINI_API_KEY manquant")
    genai.configure(api_key=settings.GEMINI_API_KEY)


def get_model():
    global _model
    if _model is None:
        init_gemini()
        _model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL or "gemini-1.5-flash"
        )
    return _model


def call_llm(prompt: str, temperature: float = 0.1, timeout_s: int = 20) -> str:
    """
    Appel générique Gemini pour les agents KnowFlow.
    - Timeout pour éviter les requêtes qui "tournent" longtemps
    - Logs pour diagnostiquer les lenteurs
    """
    model = get_model()

    start = time.time()
    logger.info("Gemini call START (len=%s)", len(prompt))

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": temperature,
                "top_p": 0.9,
                "max_output_tokens": 2048,
            },
            # évite Postman "Sending request..." infiniment
            request_options={"timeout": timeout_s},
        )

        dt = time.time() - start
        logger.info("Gemini call OK in %.2fs", dt)

        text = getattr(response, "text", None)
        if not text:
            raise LLMError("Réponse Gemini vide (response.text is empty)")
        return text

    except Exception as e:
        dt = time.time() - start
        logger.exception("Gemini call FAIL after %.2fs", dt)
        raise LLMError(f"Erreur Gemini: {e}")
