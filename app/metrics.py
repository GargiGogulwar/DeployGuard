"""Prometheus metrics. Names here are the ones used by the Grafana dashboard."""
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram
from prometheus_client import PlatformCollector

REGISTRY = CollectorRegistry(auto_describe=True)
PlatformCollector(registry=REGISTRY)

# Cross-platform process start time metric. The default ProcessCollector does not
# expose this metric on every operating system (notably Windows).
import time
PROCESS_START_TIME = Gauge(
    "process_start_time_seconds",
    "Unix timestamp when the DeployGuard process started.",
    registry=REGISTRY,
)
PROCESS_START_TIME.set(time.time())

HTTP_REQUESTS = Counter(
    "deployguard_http_requests_total",
    "Total HTTP requests handled by DeployGuard.",
    ["method", "path", "status"],
    registry=REGISTRY,
)
HTTP_LATENCY = Histogram(
    "deployguard_http_request_duration_seconds",
    "HTTP request latency in seconds.",
    ["method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
    registry=REGISTRY,
)
SERVICE_READY = Gauge(
    "deployguard_service_ready",
    "1 if the application's dependencies are healthy (readiness), else 0.",
    registry=REGISTRY,
)
BUILD_INFO = Gauge(
    "deployguard_build_info",
    "Build metadata of the running image (value is always 1).",
    ["version", "git_sha", "image_tag", "environment"],
    registry=REGISTRY,
)
DEPLOYMENTS_RECORDED = Counter(
    "deployguard_deployments_recorded_total",
    "Deployment records written, by source and status.",
    ["source", "status"],
    registry=REGISTRY,
)
