from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from .api.routes.collector import router as collector_router
from .api.routes.extraction import router as extraction_router
from .api.routes import maintenance, retrieval
from .api.routes.vectorization import router as vectorization_router
from .api.routes import query as query_router
from .api.routes.intent import router as intent_router
from .api.routes.summarizer import router as summarizer_router
from .api.routes.graph import router as graph_router

from app.observability.logging import configure_logging
from app.observability.middleware import ObservabilityMiddleware

configure_logging()

app = FastAPI(
    title="KnowFlow Backend",
    version="0.1.0",
)

app.add_middleware(ObservabilityMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

app.include_router(collector_router, prefix="/api")
app.include_router(extraction_router, prefix="/api")
app.include_router(maintenance.router, prefix="/api")
app.include_router(vectorization_router, prefix="/api")
app.include_router(retrieval.router, prefix="/api")
app.include_router(query_router.router, prefix="/api")
app.include_router(intent_router, prefix="/api")
app.include_router(summarizer_router, prefix="/api")
app.include_router(graph_router, prefix="/api")
