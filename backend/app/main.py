from fastapi import FastAPI

from .api.routes.collector import router as collector_router
from .api.routes.extraction import router as extraction_router
from .api.routes import maintenance, retrieval
from .api.routes.vectorization import router as vectorization_router
from .api.routes import query as query_router

app = FastAPI(
    title="KnowFlow Backend",
    version="0.1.0",
)

app.include_router(collector_router, prefix="/api")
app.include_router(extraction_router, prefix="/api")
app.include_router(maintenance.router, prefix="/api")
app.include_router(vectorization_router, prefix="/api")
app.include_router(retrieval.router, prefix="/api")
app.include_router(query_router.router, prefix="/api")