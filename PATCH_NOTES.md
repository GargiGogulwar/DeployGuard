# DeployGuard Patch Notes

This patch corrects deployment and test dependency issues found during review of the supplied archive.

## Changes made

1. **Ansible container health check:** changed the inspected container from `deployguard-app` (the local Compose name) to `deployguard-prod-app` (the explicit container name in `docker/docker-compose.prod.yml`). This prevents the production playbook from failing while checking the wrong container.
2. **FastAPI TestClient dependency:** replaced `httpx2==2.13.1` with `httpx==0.28.1`. FastAPI/Starlette's `TestClient` uses the `httpx` package; `httpx2` is not the correct dependency for this test setup.
3. **Deployment record commit metadata:** use the full 40-character commit SHA extracted from the immutable `sha-<commit>` image tag for both `version` and `commit_sha`, instead of truncating the SHA.
4. **Documentation:** updated the documented development dependency list.

## Validation status

Static inspection and file-level checks were performed when producing this patch. Cloud deployment was not run, and no AWS resources were created. Run the test, Compose, Terraform, and Ansible validation commands in `README.md`/`docs/` in your own environment before submission.


Additional portability fix: defined `process_start_time_seconds` explicitly so the metric exists on Windows as well as Linux, without relying on platform-specific ProcessCollector behavior.
