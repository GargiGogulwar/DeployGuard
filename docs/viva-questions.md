# Viva preparation

## CI/CD and GitHub Actions
**Q: What is CI/CD?** CI merges and automatically builds/tests every change; CD automatically releases validated artifacts (delivery = ready to release, deployment = released automatically).
**Q: Walk through your pipeline.** build → test → (iac-validate) → docker (build, check, publish on main) → deploy (opt-in, approved) with health and Prometheus verification.
**Q: How do you make deploy wait for tests?** `needs:` dependencies between jobs; a failed job skips dependents.
**Q: Why not publish from pull requests?** Untrusted code could push or exfiltrate; publish steps run only on `push` to `main`, and PR tokens from forks are read-only.
**Q: What are `permissions:` for?** They limit what `GITHUB_TOKEN` can do (least privilege). Default is `contents: read`; only the docker job gets `packages: write`.
**Q: Where are secrets stored?** GitHub Secrets (environment-scoped for `production`), injected via `env:`; GitHub masks them in logs.
**Q: What is an environment?** A named deployment target with protection rules (required reviewers) and its own secrets.
**Q: What does `concurrency` do?** Prevents overlapping runs; superseded PR runs are cancelled.

## Docker and Compose
**Q: Image vs container?** Image = immutable template; container = running instance.
**Q: Why a non-root user?** Limits damage if the app is compromised. UID 10001, `no-new-privileges`, `cap_drop: ALL`.
**Q: What does HEALTHCHECK do?** Docker runs the command periodically and marks the container healthy/unhealthy; Compose `depends_on: condition: service_healthy` uses it.
**Q: Why pin versions and use a SHA tag?** Reproducibility and traceability; `latest` moves, so you cannot tell what is running or roll back reliably.
**Q: Compose vs Kubernetes?** Compose runs multi-container apps on one host; Kubernetes adds clustering/scaling. Not needed for this scope.
**Q: Why `0.0.0.0` inside the container?** Otherwise it listens only on the container loopback and published ports cannot reach it. The host side is bound to `127.0.0.1` locally.
**Q: Where is data persisted?** Named volumes `app_data`, `prometheus_data`, `grafana_data`.

## Terraform
**Q: What is IaC?** Describing infrastructure in version-controlled code instead of console clicks.
**Q: init / plan / apply / destroy?** init downloads providers; plan previews changes; apply performs them; destroy removes everything in state.
**Q: What is state and why protect it?** The mapping of code to real resources; it can hold sensitive values, so it is git-ignored (use a remote encrypted backend in teams).
**Q: How is SSH restricted?** `ssh_allowed_cidr` variable with a validation rejecting `0.0.0.0/0`.
**Q: How do you avoid hardcoding an AMI?** SSM public parameter for Ubuntu 24.04.
**Q: IAM needed?** The operator needs EC2 and security-group permissions (see `terraform/README.md`); the instance itself has no role (least privilege).

## Ansible
**Q: Why Ansible?** Agentless, idempotent, declarative tasks over SSH.
**Q: What is idempotency?** Re-running yields the same state without repeated changes (e.g. `apt: state=present`).
**Q: How are secrets protected?** Read from environment variables, `.env` mode 0600, `no_log: true`; never in the repo.
**Q: How do you know a deployment worked?** Container health, `/health`, `/ready`, and Prometheus target `up`; any failure fails the playbook.

## Prometheus and Grafana
**Q: Pull vs push?** Prometheus pulls (scrapes) `/metrics`; a down target is itself a signal (`up == 0`).
**Q: Metric types used?** Counter (`requests_total`), histogram (`request_duration_seconds`), gauge (`service_ready`, `build_info`).
**Q: Explain `rate()` and `histogram_quantile()`.** `rate` = per-second increase of a counter over a window; `histogram_quantile(0.95, …_bucket)` estimates the 95th-percentile from bucket rates.
**Q: Why label by route template?** Raw URLs would create unbounded label cardinality.
**Q: Liveness vs readiness?** Liveness = process alive; readiness = dependencies OK and able to serve.
**Q: Is there self-healing?** No. Docker restarts crashed containers; there is no automated remediation or Alertmanager routing.

## Security and troubleshooting
**Q: How are secrets kept out of the UI/logs?** Fixed allow-list of fields in `/api/status`; token never returned; test asserts it.
**Q: Security headers?** `nosniff`, `X-Frame-Options: DENY`, CSP `default-src 'self'`, `Referrer-Policy`.
**Q: Pipeline failed at test — what now?** Open the job log, reproduce locally with `python -m pytest`, fix, push.
**Q: Prometheus target is DOWN?** `docker compose ps`, `docker compose logs deployguard`, check network name/port in `prometheus.yml`.
**Q: Ansible UNREACHABLE?** Key permissions, security-group CIDR (your IP changed?), username `ubuntu`.
**Q: What did you NOT verify?** Be candid: say what you ran yourself (see README §20 and your own screenshots).
