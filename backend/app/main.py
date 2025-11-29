# app/main.py
from fastapi import FastAPI

from .api.routes.collector import router as collector_router
from .core.db import Base, engine
from .memory import models  # pour que SQLAlchemy voie Document
from .api.routes.extraction import router as extraction_router

app = FastAPI(
    title="KnowFlow Backend",
    version="0.1.0",
)

# Création des tables au démarrage (en dev)
Base.metadata.create_all(bind=engine)

# Routes
app.include_router(collector_router, prefix="/api")
app.include_router(extraction_router, prefix="/api")