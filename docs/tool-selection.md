# Tool selection and justification (Rubric criterion 1)

| Need | Chosen | Alternatives considered | Reason for the choice |
|---|---|---|---|
| Backend | FastAPI | Flask, Django | Built-in request validation and OpenAPI docs, first-class `TestClient`; Django is heavier than needed |
| CI/CD | GitHub Actions | Jenkins, GitLab CI | No server to run, free for the repo, native secrets/environments, same place as the code and registry |
| Container | Docker | Podman | Ubiquitous; matches all course material and GitHub runners |
| Local orchestration | Docker Compose | Kubernetes/minikube | Core requirement is 3 services on 1 host; Kubernetes adds cost and complexity without benefit here |
| Registry | GHCR | Docker Hub, ECR | Authenticates with `GITHUB_TOKEN`; no extra account or AWS cost |
| IaC | Terraform | CloudFormation, manual console | Declarative, reviewable plan before change, portable skills |
| Config/deploy | Ansible | Shell scripts, Chef/Puppet | Agentless over SSH, idempotent modules, readable |
| Cloud | AWS EC2 Ubuntu | ECS, EKS, Lightsail | Single VM is cheapest and simplest; fewest AWS services |
| Metrics | Prometheus | Datadog, CloudWatch | Open source, pull model shows "target down" directly, PromQL |
| Dashboards | Grafana | Kibana | Native Prometheus data source, file provisioning |
| Persistence | SQLite | PostgreSQL | Tiny dataset; no extra container to run |

## Design decisions per stage
* **Source:** trigger on push/PR to `main`; `concurrency` cancels superseded PR runs.
* **Build:** `pip check`, byte-compile, import check catch broken dependencies before tests.
* **Test:** pytest + coverage; failure stops the pipeline (`needs:`).
* **Containerize:** non-root user, health check, build args carry commit SHA and test status; container smoke test before publishing.
* **Publish:** only on `push` to `main`; `packages: write` only on that job; tags are `sha-<full commit>`.
* **Deploy:** opt-in (`DEPLOY_ENABLED`), protected `production` environment, immutable tag, health + Prometheus verification.
* **Monitor:** readiness gauge, request counter/latency histogram, alert rule for target down.

## Python version note
The brief asks for Python 3.14.6 "if all dependencies support it". It could not be confirmed here (the build environment only had Python 3.12.3), so the Dockerfile and CI use **3.12** (`PYTHON_VERSION`). To try 3.14: set `PYTHON_VERSION` in `.github/workflows/ci-cd.yml` and build with `--build-arg PYTHON_VERSION=3.14`; if tests and `pip check` pass, keep it. Do not claim 3.14 in your report unless you ran it.

## Dependency pins
`fastapi==0.143.0`, `uvicorn[standard]==0.54.0`, `jinja2==3.1.6`, `prometheus-client==0.26.0`; dev: `pytest==9.1.1`, `httpx==0.28.1` (FastAPI/Starlette TestClient transport), `pytest-cov==7.1.0`. Images: `prom/prometheus:v2.55.1`, `grafana/grafana:11.3.0`. Action majors were looked up from GitHub tags on the build date; re-check them occasionally.
