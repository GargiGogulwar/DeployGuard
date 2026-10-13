# Monitoring guide

## Verify after `docker compose up -d --build`
1. **App metrics:** `curl -s http://127.0.0.1:8000/metrics | grep deployguard_http_requests_total` — lines with `path="/metrics"` etc.
2. **Prometheus targets:** open `http://127.0.0.1:9090/targets` — job `deployguard` state **UP**. Query `up{job="deployguard"}` → `1`.
3. **Grafana:** `http://127.0.0.1:3000` → Dashboards → DeployGuard → **DeployGuard Overview**. Generate traffic:
   ```bash
   for i in $(seq 1 50); do curl -s localhost:8000/health >/dev/null; curl -s localhost:8000/nope >/dev/null; done
   ```
4. **Alerts:** `http://127.0.0.1:9090/alerts` (rules loaded; no notifications are configured).

## Panels and queries (metric names are checked by `tests/test_monitoring_config.py`)
| Panel | PromQL |
|---|---|
| Service availability | `min(up{job="deployguard"})` |
| Readiness | `min(deployguard_service_ready)` |
| Uptime | `time() - max(process_start_time_seconds{job="deployguard"})` |
| Requests (5 m) | `sum(increase(deployguard_http_requests_total[5m]))` |
| Request rate by status | `sum by (status) (rate(deployguard_http_requests_total[1m]))` |
| Error rate | `(sum(rate(deployguard_http_requests_total{status=~"5.."}[1m])) or vector(0)) / sum(rate(deployguard_http_requests_total[1m]))` |
| Latency p50/p95/p99 | `histogram_quantile(0.95, sum by (le) (rate(deployguard_http_request_duration_seconds_bucket[1m])))` |
| Requests by path | `sum by (path) (rate(deployguard_http_requests_total[1m]))` |
| Running build | `deployguard_build_info` |

Note: 404s are client errors, so they appear in "rate by status" but not in the 5xx error rate.

## Controlled failure and recovery
```bash
docker compose stop deployguard        # 1. simulate outage (safe; data volume kept)
# 2. within ~5-20 s: Prometheus target DOWN; Grafana availability = DOWN;
#    http://127.0.0.1:9090/alerts shows DeployGuardDown pending -> firing (after 15 s)
curl -sS http://127.0.0.1:8000/health   # connection refused (expected)
docker compose start deployguard       # 3. restore
docker compose ps                      # wait until deployguard is (healthy)
curl -fsS http://127.0.0.1:8000/health # 4. verify recovery; target UP again, alert resolved
```
Optional readiness failure test: not exposed by a switch on purpose; the automated test `test_ready_returns_503_when_database_fails` covers it.

Honesty note: Docker's `restart: unless-stopped` will restart a *crashed* container, but a container you stopped stays stopped. That is Docker's restart policy, not a self-healing system, and nothing in this project claims otherwise.

*In the build environment the same scenario was verified with the app process and a real Prometheus binary (up 1 → 0, alert firing → up 1); the Docker version of the steps above still needs to be run by you.*
