# FA 2 rubric mapping

| Criterion | Marks | Deliverables that address it | Where |
|---|---|---|---|
| 1. Selection of methods, tools and design | 3 | Justified tool table with alternatives; per-stage design; honest limitations | `docs/tool-selection.md`, `docs/architecture.md`, `docs/pipeline.md`, README §6-8, report §5-7 |
| 2. Implementation (working end-to-end CI/CD) | 5 | App + 19 tests; GitHub Actions (build, test, containerize, publish, deploy, verify); Dockerfile + Compose; Terraform; Ansible; Prometheus + Grafana + alert; failure/recovery procedure | `app/`, `tests/`, `.github/workflows/ci-cd.yml`, `Dockerfile`, `docker-compose.yml`, `terraform/`, `ansible/`, `monitoring/`, `docs/monitoring-guide.md` |
| 3. Timely submission | 2 | README, FA 2 report, deployment guide, demo plan, screenshot checklist, viva Q&A; all modules present | `README.md`, `docs/fa2-report.md`, `docs/demo-plan.md`, `docs/screenshot-checklist.md`, `docs/viva-questions.md` |

Evidence you must still produce: screenshots/logs from your own runs and submission before the deadline (`<DEADLINE>`). Be ready to state which parts you ran locally, in GitHub Actions and in AWS.
