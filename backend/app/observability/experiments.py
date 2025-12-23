from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Dict, Optional

try:
    import mlflow
except Exception:  # pragma: no cover
    mlflow = None  # type: ignore


class ExperimentTracker:
    def __init__(self) -> None:
        self.enabled = bool(os.getenv("MLFLOW_TRACKING_URI")) and mlflow is not None
        if self.enabled:
            mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
            exp = os.getenv("MLFLOW_EXPERIMENT_NAME", "knowflow")
            mlflow.set_experiment(exp)

    @contextmanager
    def run(self, *, name: str, params: Optional[Dict[str, Any]] = None, tags: Optional[Dict[str, str]] = None):
        if not self.enabled or mlflow is None:
            yield None
            return

        with mlflow.start_run(run_name=name):
            if tags:
                mlflow.set_tags(tags)
            if params:
                mlflow.log_params(params)
            yield mlflow

    def log_metrics(self, metrics: Dict[str, float]) -> None:
        if self.enabled and mlflow is not None:
            mlflow.log_metrics(metrics)
