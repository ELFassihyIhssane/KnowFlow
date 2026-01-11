from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Dict, Optional

try:
    from langfuse import Langfuse
except Exception:  
    Langfuse = None  


class Tracer:
    def __init__(self) -> None:
        self.enabled = bool(os.getenv("LANGFUSE_PUBLIC_KEY")) and Langfuse is not None
        self.client = None
        if self.enabled:
            self.client = Langfuse(
                public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
                secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
                host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
            )

    @contextmanager
    def trace(self, *, name: str, user_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        if not self.enabled or self.client is None:
            yield None
            return

        t = self.client.trace(name=name, user_id=user_id, metadata=metadata or {})
        try:
            yield t
        finally:
            t.update(status="success")

    def span(self, trace_obj, *, name: str, metadata: Optional[Dict[str, Any]] = None):
        if trace_obj is None:
            return _NullSpan()
        return trace_obj.span(name=name, metadata=metadata or {})


class _NullSpan:
    def __enter__(self):  
        return None

    def __exit__(self, exc_type, exc, tb):  
        return False
