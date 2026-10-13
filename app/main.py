"""DeployGuard FastAPI application."""
import logging
import secrets
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel, Field

from app import metrics
from app.config import Settings, get_settings
from app.store import DeploymentStore

BASE_DIR = Path(__file__).resolve().parent
logger = logging.getLogger("deployguard")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class DeploymentIn(BaseModel):
    """Payload for POST /api/deployments (token protected)."""

    version: str = Field(min_length=1, max_length=40, pattern=r"^[A-Za-z0-9._+-]+$")
    image_tag: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:/@-]+$")
    commit_sha: str = Field(min_length=7, max_length=40, pattern=r"^[0-9a-fA-F]+$")
    environment: str = Field(min_length=1, max_length=30, pattern=r"^[A-Za-z0-9_-]+$")
    status: Literal["started", "success", "failed"]
    source: Literal["simulated", "ci-cd"]
    note: str = Field(default="", max_length=200)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    store = DeploymentStore(settings.db_path)
    app.state.settings = settings
    app.state.store = store
    app.state.started_at = time.time()
    metrics.BUILD_INFO.clear()
    metrics.BUILD_INFO.labels(
        settings.version, settings.git_sha, settings.image_tag, settings.environment
    ).set(1)
    metrics.SERVICE_READY.set(1 if store.ping() else 0)
    # Factual runtime event only: this process started. It is NOT a deployment claim.
    store.add(
        version=settings.version, image_tag=settings.image_tag, commit_sha=settings.git_sha,
        environment=settings.environment, status="started", source="runtime",
        note="Application process started.",
    )
    metrics.DEPLOYMENTS_RECORDED.labels("runtime", "started").inc()
    logger.info("DeployGuard %s started (env=%s)", settings.version, settings.environment)
    yield
    store.close()


app = FastAPI(title="DeployGuard", version=get_settings().version, lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'",
}


@app.middleware("http")
async def observe(request: Request, call_next):
    start = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
    except Exception:  # noqa: BLE001 - log type only, never request data
        logger.exception("Unhandled error")
        response = JSONResponse({"detail": "Internal server error"}, status_code=500)
    # Use the route template (not the raw URL) to keep label cardinality bounded.
    route = request.scope.get("route")
    path = getattr(route, "path", "unmatched")
    elapsed = time.perf_counter() - start
    metrics.HTTP_REQUESTS.labels(request.method, path, str(status)).inc()
    metrics.HTTP_LATENCY.labels(request.method, path).observe(elapsed)
    for k, v in SECURITY_HEADERS.items():
        response.headers[k] = v
    if path.startswith("/api") or path in ("/health", "/ready", "/metrics"):
        response.headers["Cache-Control"] = "no-store"
    return response


def get_store(request: Request) -> DeploymentStore:
    return request.app.state.store


def require_token(x_api_token: Optional[str] = Header(default=None)) -> None:
    expected = get_settings().api_token
    if not expected:
        raise HTTPException(403, "Recording deployments is disabled (no API token configured).")
    if not x_api_token or not secrets.compare_digest(x_api_token, expected):
        raise HTTPException(401, "Invalid or missing X-API-Token header.")


def _status_payload(request: Request) -> dict:
    s: Settings = request.app.state.settings
    store: DeploymentStore = request.app.state.store
    ready = store.ping()
    metrics.SERVICE_READY.set(1 if ready else 0)
    return {
        "application": s.app_name,
        "version": s.version,
        "environment": s.environment,
        "git_sha": s.git_sha,
        "image_tag": s.image_tag,
        "build_time": s.build_time,
        "ci_test_status": s.ci_test_status,
        "uptime_seconds": int(time.time() - request.app.state.started_at),
        "health": "ok",
        "ready": ready,
        "database": "ok" if ready else "unavailable",
        "latest_deployment": store.latest(),
        "latest_ci_cd_deployment": store.latest(source="ci-cd"),
        "note": "Records with source 'simulated' or 'runtime' are NOT real deployments.",
    }


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "index.html", {"settings": request.app.state.settings})


@app.get("/health")
async def health():
    """Liveness: the process is up and serving requests."""
    return {"status": "ok"}


@app.get("/ready")
async def ready(request: Request):
    """Readiness: dependencies (database) are usable."""
    ok = request.app.state.store.ping()
    metrics.SERVICE_READY.set(1 if ok else 0)
    body = {"status": "ready" if ok else "not_ready", "checks": {"database": "ok" if ok else "failed"}}
    return JSONResponse(body, status_code=200 if ok else 503)


@app.get("/api/status")
async def api_status(request: Request):
    return _status_payload(request)


@app.get("/api/deployments")
async def list_deployments(
    store: DeploymentStore = Depends(get_store),
    limit: int = Query(20, ge=1, le=100),
    source: Optional[Literal["runtime", "simulated", "ci-cd"]] = None,
):
    items = store.list(limit=limit, source=source)
    return {"count": len(items), "items": items}


@app.post("/api/deployments", status_code=201, dependencies=[Depends(require_token)])
async def record_deployment(payload: DeploymentIn, store: DeploymentStore = Depends(get_store)):
    """Record a deployment event. Requires X-API-Token.

    source='simulated' is for demos and must not be presented as a real deployment.
    source='ci-cd' is used by the pipeline/Ansible after a real deployment step.
    """
    rec = store.add(**payload.model_dump())
    metrics.DEPLOYMENTS_RECORDED.labels(payload.source, payload.status).inc()
    return rec


@app.get("/metrics", include_in_schema=False)
async def metrics_endpoint():
    return Response(generate_latest(metrics.REGISTRY), media_type=CONTENT_TYPE_LATEST)
