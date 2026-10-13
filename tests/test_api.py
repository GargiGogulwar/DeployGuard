import re

VALID = {
    "version": "1.0.0", "image_tag": "sha-abcdef1", "commit_sha": "abcdef1",
    "environment": "staging", "status": "success", "source": "simulated", "note": "demo",
}
H = {"X-API-Token": "test-token"}


def test_dashboard_html_and_security_headers(client):
    r = client.get("/")
    assert r.status_code == 200 and "text/html" in r.headers["content-type"]
    assert "DeployGuard" in r.text
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["x-frame-options"] == "DENY"
    assert "default-src 'self'" in r.headers["content-security-policy"]


def test_static_assets_served(client):
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/style.css").status_code == 200


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json() == {"status": "ok"}


def test_ready_ok(client):
    r = client.get("/ready")
    assert r.status_code == 200 and r.json()["status"] == "ready"


def test_ready_returns_503_when_database_fails(client):
    client.app.state.store.close()  # simulate dependency failure
    r = client.get("/ready")
    assert r.status_code == 503 and r.json()["checks"]["database"] == "failed"


def test_status_api(client):
    d = client.get("/api/status").json()
    assert d["application"] == "DeployGuard" and d["health"] == "ok" and d["ready"] is True
    assert d["git_sha"] == "abc1234" and d["ci_test_status"] == "passed"
    assert d["latest_deployment"]["source"] == "runtime"
    assert d["latest_ci_cd_deployment"] is None  # nothing real recorded yet


def test_status_does_not_leak_secrets(client):
    body = client.get("/api/status").text + client.get("/").text
    assert "test-token" not in body and "api_token" not in body


def test_deployments_history_has_startup_record(client):
    d = client.get("/api/deployments").json()
    assert d["count"] >= 1 and d["items"][0]["source"] == "runtime"


def test_deployments_query_validation(client):
    assert client.get("/api/deployments?limit=0").status_code == 422
    assert client.get("/api/deployments?limit=1000").status_code == 422
    assert client.get("/api/deployments?source=bogus").status_code == 422
    assert client.get("/api/deployments?limit=5&source=runtime").status_code == 200


def test_record_deployment_success(client):
    r = client.post("/api/deployments", json=VALID, headers=H)
    assert r.status_code == 201 and r.json()["source"] == "simulated"
    items = client.get("/api/deployments?source=simulated").json()["items"]
    assert len(items) == 1


def test_ci_cd_record_updates_status(client):
    client.post("/api/deployments", json={**VALID, "source": "ci-cd"}, headers=H)
    assert client.get("/api/status").json()["latest_ci_cd_deployment"]["status"] == "success"


def test_record_requires_token(client):
    assert client.post("/api/deployments", json=VALID).status_code == 401
    assert client.post("/api/deployments", json=VALID, headers={"X-API-Token": "nope"}).status_code == 401


def test_record_disabled_without_configured_token(client, monkeypatch):
    monkeypatch.delenv("DEPLOYGUARD_API_TOKEN")
    assert client.post("/api/deployments", json=VALID, headers=H).status_code == 403


def test_record_rejects_invalid_input(client):
    for bad in (
        {**VALID, "status": "exploded"},
        {**VALID, "source": "runtime"},          # runtime records cannot be forged
        {**VALID, "commit_sha": "not-hex!"},
        {**VALID, "version": "<script>"},
        {**VALID, "note": "x" * 500},
        {k: v for k, v in VALID.items() if k != "image_tag"},
    ):
        assert client.post("/api/deployments", json=bad, headers=H).status_code == 422


def test_unknown_route_404(client):
    assert client.get("/does-not-exist").status_code == 404


def test_metrics_endpoint_and_names(client):
    client.get("/health")
    client.get("/does-not-exist")
    r = client.get("/metrics")
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/plain")
    t = r.text
    for name in (
        "deployguard_http_requests_total", "deployguard_http_request_duration_seconds_bucket",
        "deployguard_service_ready", "deployguard_build_info", "process_start_time_seconds",
    ):
        assert name in t, name
    assert re.search(r'deployguard_http_requests_total\{[^}]*path="/health"[^}]*status="200"\} [1-9]', t)
    assert 'path="unmatched"' in t and 'status="404"' in t  # bounded label cardinality
    assert "test-token" not in t


def test_5xx_is_counted_and_returned_as_json(client, monkeypatch):
    def boom():
        raise RuntimeError("boom")

    monkeypatch.setattr("app.main.get_settings", boom)
    # /api/deployments POST calls get_settings via require_token -> unhandled error -> 500
    r = client.post("/api/deployments", json=VALID, headers=H)
    assert r.status_code == 500 and r.json() == {"detail": "Internal server error"}
    monkeypatch.undo()
    assert 'status="500"' in client.get("/metrics").text
