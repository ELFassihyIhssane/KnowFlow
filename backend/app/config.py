from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    
    DATABASE_URL: str
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str | None = None

    
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str | None = "gemini-2.0-flash"

   
    LOG_LEVEL: str = "INFO"

    
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"
    LANGFUSE_PUBLIC_KEY: str | None = None
    LANGFUSE_SECRET_KEY: str | None = None

    
    MLFLOW_TRACKING_URI: str | None = None
    MLFLOW_EXPERIMENT_NAME: str = "knowflow"

    class Config:
        env_file = ".env"  
        extra = "ignore"   


settings = Settings()
