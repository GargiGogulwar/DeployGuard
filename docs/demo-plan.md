# Demonstration plan (≈10 minutes)

Prepare: repo pushed to GitHub, `.env` created, Docker running, stack **not** yet started, browser tabs ready.

| # | Action / command | What you should see |
|---|---|---|
| 1 | Edit `app/main.py` or a template (e.g. change the dashboard subtitle), then `git add -A && git commit -m "demo: change" && git push origin main` | Push accepted |
| 2 | GitHub → **Actions** tab | A new "DeployGuard CI/CD" run starts |
| 3 | Open the run | `build` ✔ → `test` ✔ (pytest summary, 19 passed) and `iac-validate` ✔ |
| 4 | `docker` job logs | Image build, "container user id: 10001", health/ready/metrics curl output |
| 5 | Same job, publish steps | Run on `main` push only; **Packages** shows `sha-<commit>` (on a PR these steps are skipped — show a PR run to prove it) |
| 6 | `deploy` job | Skipped unless `DEPLOY_ENABLED=true`; if enabled it waits for approval, then Ansible output shows containers healthy |
| 7 | Local: `docker compose up -d --build && docker compose ps` | 3 services, `(healthy)` |
| 8 | `curl -fsS localhost:8000/health` and `curl -s localhost:8000/api/status` | `{"status":"ok"}`; JSON with version, commit, ready=true |
| 9 | `http://localhost:9090/targets` | `deployguard` **UP** |
| 10 | Grafana → DeployGuard Overview; run the traffic loop from `monitoring-guide.md` | Availability UP, request-rate and latency lines moving |
| 11 | `docker compose stop deployguard` | Within ~20 s: target DOWN, availability DOWN, `DeployGuardDown` firing |
| 12 | `docker compose start deployguard` | Healthy again; availability UP; alert resolves |
| 13 | Show dashboard history table | `runtime` rows labelled as process starts; explain `simulated` vs `ci-cd` |

Fallback if GitHub or the network is down: run steps 7-13 only and show the saved screenshots plus `python -m pytest`.
