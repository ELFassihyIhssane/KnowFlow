from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- Core ---
    DATABASE_URL: str
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str | None = None

    # --- LLM ---
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str | None = "gemini-2.0-flash"

    # --- Observability ---
    LOG_LEVEL: str = "INFO"

    # Langfuse (optional)
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"
    LANGFUSE_PUBLIC_KEY: str | None = None
    LANGFUSE_SECRET_KEY: str | None = None

    # MLflow (optional)
    MLFLOW_TRACKING_URI: str | None = None
    MLFLOW_EXPERIMENT_NAME: str = "knowflow"

    class Config:
        env_file = ".env"  # Lecture du fichier .env à la racine du backend
        extra = "ignore"   # ✅ évite que ton app crash si tu ajoutes d'autres vars plus tard


settings = Settings()
