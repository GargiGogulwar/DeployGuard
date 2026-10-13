# CI/CD pipeline (`.github/workflows/ci-cd.yml`)

| Stage | Job | Needs | Runs on | Key steps |
|---|---|---|---|---|
| 1-2 Source, Build | `build` | – | push, PR | checkout, setup Python, install, `pip check`, compileall, import check |
| 3 Test | `test` | build | push, PR | `pytest --cov=app` (fails workflow on any failure) |
| – Validation | `iac-validate` | build | push, PR | compose config, promtool rules, `terraform fmt/validate`, Ansible syntax check |
| 4 Containerize | `docker` | test | push, PR | build image, non-root check, run container, curl `/health` `/ready` `/metrics`; **on main push only:** GHCR login + push `sha-<commit>` |
| 5-6 Deploy, Monitor | `deploy` | docker, iac-validate | main push + `DEPLOY_ENABLED=true` + environment approval | open SSH for runner IP, Ansible deploy, verify health/readiness/Prometheus target, close SSH |

## Why this order
Cheap checks run first; images are built only from tested code; deployment needs a published immutable image and valid IaC.

## Security properties
* Top-level `permissions: contents: read`; `packages: write` only in `docker` and used only when `publish == true` (push to `main`). Fork PRs have a read-only token anyway.
* No `pull_request_target`; no secrets reach PR code.
* Secrets are passed through `env:` (masked in logs). Ansible secret tasks use `no_log`.
* The deploy job opens port 22 to the runner's IP /32 using AWS credentials limited to one security group, and revokes it in an `if: always()` step. This keeps SSH off `0.0.0.0/0` even with GitHub-hosted runners (whose IPs are dynamic).
* The image tag is the commit SHA; the playbook refuses `latest`.

## Limitations (explicit)
* The deploy job and GHCR publishing were **not executed** in the build environment; you must run them on your own repo.
* Host key is trusted on first use via `ssh-keyscan`; for stricter handling store the host key as a secret.
* Access keys are long-lived secrets; GitHub OIDC with an IAM role is the better production option.
* Docker layer caching uses the GitHub cache (`type=gha`).

## Local equivalents
`python -m pytest` (test) · `docker build -t deployguard:local .` (containerize) · `docker compose up -d --build` (deploy locally) · Prometheus/Grafana on localhost (monitor).
