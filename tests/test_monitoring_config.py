"""Guards against Grafana/Prometheus drifting away from the metrics the app really exposes."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMQL_FUNCS = {"sum", "rate", "increase", "histogram_quantile", "by", "time", "max", "min", "vector",
                "or", "le", "status", "path", "job", "up"}
PROMETHEUS_GENERATED = {"up"}


def _exprs():
    dash = json.loads((ROOT / "monitoring/grafana/dashboards/deployguard-overview.json").read_text())
    out = [t["expr"] for p in dash["panels"] for t in p["targets"]]
    out += re.findall(r"expr:\s*>?\s*(.+?)\n\s*for:", (ROOT / "monitoring/alerts.yml").read_text(), re.S)
    return out


def test_every_metric_used_in_queries_exists(client):
    exposed = client.get("/metrics").text
    client.get("/health")  # make sure counters have samples
    exposed = client.get("/metrics").text
    names = set()
    for e in _exprs():
        names |= set(re.findall(r"\b([a-z][a-z0-9_]*(?:_total|_bucket|_ready|_info|_seconds|_time_seconds))\b", e))
    names -= PROMETHEUS_GENERATED
    assert names, "no metric names found"
    for n in names:
        assert re.search(rf"^{re.escape(n)}[{{ ]", exposed, re.M), f"{n} is queried but not exposed"


def test_prometheus_scrapes_the_documented_target_and_path():
    cfg = (ROOT / "monitoring/prometheus.yml").read_text()
    assert "deployguard:8000" in cfg and "/metrics" in cfg
