# DeployGuard — Automated CI/CD and Deployment Monitoring Platform

**Course:** PEC 4 – DevOps · **Assessment:** Formative Assessment 2 (10 marks)
**Student:** `<NAME>` · **Roll/PRN:** `<ROLL>` · **Section:** `<SECTION>` · **Faculty:** `<FACULTY NAME>` · **Date:** `<DATE>`
**Repository:** `<GITHUB URL>`

## 1. Abstract
DeployGuard is a FastAPI application together with an automated delivery pipeline. GitHub Actions validates, builds and tests the code, packages it into a Docker image, publishes an immutable image to GitHub Container Registry, and (optionally) deploys it to an AWS EC2 Ubuntu server provisioned with Terraform and configured with Ansible. Prometheus and Grafana monitor service availability, traffic, errors and latency. The complete stack also runs locally with Docker Compose.

## 2. Problem statement
Manual deployments are error-prone: configuration drift, inconsistent environments, failed releases and late detection of outages. An automated, observable pipeline reduces these risks.

## 3. Objectives
(1) Automate build and test; (2) containerize reproducibly; (3) deploy only validated, immutable artifacts; (4) provision infrastructure as code; (5) monitor health and performance and demonstrate failure detection and recovery.

## 4. System architecture
See `docs/architecture.md` and the Mermaid diagrams in the README: developer → GitHub → Actions → GHCR → EC2 (Docker Compose: DeployGuard, Prometheus, Grafana), with Terraform creating the EC2 host and Ansible deploying to it.

## 5. Tool selection and justification
Summarised from `docs/tool-selection.md`: FastAPI (validation, testability), pytest (standard testing), GitHub Actions (integrated, no server), Docker/Compose (reproducible packaging, simple orchestration), GHCR (free, token auth), Terraform (declarative, previewable IaC), Ansible (agentless, idempotent), Prometheus/Grafana (open-source pull-based monitoring). Kubernetes was deliberately excluded as unnecessary for a single-host system.

## 6. Methodology
Iterative: build the application and tests first; containerize; add the pipeline; add monitoring; add IaC and configuration management; validate each layer with linters and live tests; document. Local-first, so that the core demonstration needs no paid service.

## 7. Implementation details
* **Application:** endpoints `/`, `/health`, `/ready`, `/api/status`, `/api/deployments` (GET, token-protected POST), `/metrics`; SQLite history with honest `source` labels (`runtime`, `simulated`, `ci-cd`); security headers; validated input.
* **Pipeline:** jobs `build`, `test`, `iac-validate`, `docker`, `deploy` with explicit `needs:`; least-privilege `permissions`; publish only on push to `main`; deploy opt-in with protected environment.
* **Container:** Python 3.12-slim, non-root UID 10001, health check, build args carrying commit SHA and CI test status.
* **Compose:** isolated network, named volumes, health-gated start order, configurable ports.
* **Terraform:** EC2 + security group, SSH restricted to a validated CIDR, IMDSv2, encrypted volume.
* **Ansible:** installs Docker, ships configuration, deploys an immutable tag, verifies health, readiness and the Prometheus target.
* **Monitoring:** custom counters/histograms/gauges, 9-panel Grafana dashboard, alert rules (`DeployGuardDown`, `DeployGuardNotReady`, `DeployGuardHighErrorRate`).

## 8. Testing and results
Automated suite: 19 pytest tests covering the dashboard, static assets, health, readiness (success and 503 failure path), status, history (including query validation), token-protected recording (success, 401, 403, 422 cases), 404 handling, 5xx counting, metric names, secret non-disclosure, and consistency between Grafana/alert queries and exposed metrics.

Results obtained by the author of this report in the build environment (Python 3.12.3, Linux, no Docker/AWS):

| Check | Result |
|---|---|
| `pytest --cov=app` | 19 passed, 100 % line coverage |
| Pinned requirements in a clean virtualenv, `pip check` | OK |
| Live app + Prometheus 2.55.1: targets | `deployguard` up, `prometheus` up |
| All 11 Grafana panel queries evaluated in Prometheus | All returned data |
| Failure drill (stop app / restart) | `up` 1 → 0, `DeployGuardDown` firing → `up` 1, ready 1 |
| `promtool`, `docker compose config` (2 files), `hadolint`, `actionlint`, `yamllint`, `tofu fmt`, `ansible --syntax-check`, `ansible-lint` | All passed |

Results from your own runs (fill in; do not copy numbers you did not obtain):

| Check | Date/time | Result | Evidence file |
|---|---|---|---|
| GitHub Actions run URL | `<>` | `<>` | `03-actions-run-overview.png` |
| `docker build` / `compose up` | `<>` | `<>` | `08`, `09` |
| Prometheus target / Grafana | `<>` | `<>` | `13`, `14` |
| Failure and recovery | `<>` | `<>` | `15`, `16` |
| Terraform / Ansible (if performed) | `<>` | `<>` | `17`, `18` |

## 9. CI/CD pipeline
See `docs/pipeline.md` for the stage table and job dependencies and the workflow diagram in the README.

## 10. Deployment and monitoring
Local: `docker compose up -d --build`. Cloud (optional): `terraform apply` → Ansible deploy of `ghcr.io/<owner>/<repo>:sha-<commit>` → verification via `/health`, `/ready` and Prometheus targets. Monitoring procedure and failure drill are in `docs/monitoring-guide.md`.

## 11. Limitations
Single instance and environment; HTTP without TLS; no Alertmanager notifications; no automatic rollback or self-healing; long-lived AWS keys in the optional CD job; Python 3.14 not tested; cloud deployment, GHCR publishing and Docker execution were not executed during development of the code and must be demonstrated by the student.

## 12. Conclusion
DeployGuard shows the full software delivery lifecycle with automation, immutable artifacts, security-conscious defaults and observable behaviour. Future work: Alertmanager, TLS, rolling/blue-green deployment with rollback, OIDC authentication to AWS, image vulnerability scanning and signing.

## 13. References
1. FastAPI documentation — https://fastapi.tiangolo.com
2. GitHub Actions documentation — https://docs.github.com/actions
3. GitHub Container Registry — https://docs.github.com/packages
4. Docker and Compose documentation — https://docs.docker.com
5. Terraform AWS provider — https://registry.terraform.io/providers/hashicorp/aws
6. Ansible documentation — https://docs.ansible.com
7. Prometheus documentation — https://prometheus.io/docs
8. Grafana documentation — https://grafana.com/docs

## Rubric mapping
See `docs/rubric-mapping.md`.
