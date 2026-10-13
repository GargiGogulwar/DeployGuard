# Screenshot checklist (capture your own; none are provided)

Save under `docs/evidence/` (create it) with these names.

| File | What to capture |
|---|---|
| `01-repo-structure.png` | GitHub repo root showing folders |
| `02-pytest-pass.png` | Terminal: `python -m pytest --cov=app` all passed |
| `03-actions-run-overview.png` | Actions run graph with all jobs green |
| `04-actions-test-job.png` | Expanded `test` job log |
| `05-actions-docker-job.png` | Container checks and publish steps |
| `06-ghcr-package.png` | Package page with `sha-<commit>` tag |
| `07-pr-no-publish.png` | A PR run showing publish/deploy skipped |
| `08-docker-build.png` | `docker build` success |
| `09-compose-ps-healthy.png` | `docker compose ps` all healthy |
| `10-dashboard.png` | DeployGuard dashboard in the browser |
| `11-health-status-curl.png` | curl of `/health`, `/ready`, `/api/status` |
| `12-metrics-endpoint.png` | `/metrics` output |
| `13-prometheus-targets-up.png` | Prometheus targets page, UP |
| `14-grafana-dashboard.png` | Grafana Overview with data |
| `15-failure-down.png` | Target DOWN + Grafana DOWN + firing alert |
| `16-recovery-up.png` | Recovered state |
| `17-terraform-plan.png` | `terraform plan` (optional cloud) |
| `18-ansible-run.png` | Ansible recap `failed=0` (optional cloud) |
| `19-cloud-app.png` | App/Grafana via EC2 public IP (optional cloud) |
| `20-terraform-destroy.png` | Cleanup evidence (optional cloud) |

Blur or crop IPs, tokens, account IDs and any secret before submitting.
