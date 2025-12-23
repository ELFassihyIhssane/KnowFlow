from __future__ import annotations

from prometheus_client import Counter, Histogram

REQUESTS_TOTAL = Counter(
    "knowflow_requests_total",
    "Total number of requests",
    ["endpoint", "status"],
)

REQUEST_LATENCY_MS = Histogram(
    "knowflow_request_latency_ms",
    "Request latency in milliseconds",
    ["endpoint"],
    buckets=(50, 100, 200, 400, 800, 1500, 3000, 6000, 10000, 20000),
)

AGENT_LATENCY_MS = Histogram(
    "knowflow_agent_latency_ms",
    "Agent latency in milliseconds",
    ["agent_name"],
    buckets=(10, 25, 50, 100, 200, 400, 800, 1500, 3000, 6000, 10000),
)

AGENT_CALLS_TOTAL = Counter(
    "knowflow_agent_calls_total",
    "Total number of agent calls",
    ["agent_name", "status"],
)
