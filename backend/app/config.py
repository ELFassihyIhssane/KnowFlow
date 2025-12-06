from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str | None = None

    class Config:
        env_file = ".env"  # Lecture du fichier .env à la racine du backend

settings = Settings()
