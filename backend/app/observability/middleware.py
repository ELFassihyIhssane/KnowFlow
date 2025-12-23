from __future__ import annotations

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.observability.logging import get_logger
from app.observability.metrics import REQUESTS_TOTAL, REQUEST_LATENCY_MS

log = get_logger("knowflow.http")


class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()
        status = "500"
        try:
            response = await call_next(request)
            status = str(response.status_code)
            return response
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            endpoint = request.url.path

            REQUESTS_TOTAL.labels(endpoint=endpoint, status=status).inc()
            REQUEST_LATENCY_MS.labels(endpoint=endpoint).observe(elapsed_ms)

            log.info(
                "request",
                method=request.method,
                path=endpoint,
                status=int(status),
                latency_ms=round(elapsed_ms, 2),
            )
