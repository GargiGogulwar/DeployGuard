# Ansible deployment

## Prerequisites
Control machine with Linux/macOS/WSL, `pip install ansible` (or `ansible-core` + `ansible-galaxy collection install -r requirements.yml`), an Ubuntu 22.04/24.04 host reachable over SSH (user `ubuntu`), and a published image tag `ghcr.io/<owner>/<repo>:sha-<commit>`.

## Configure
```bash
cp inventory.ini.example inventory.ini        # set ansible_host and key path (git-ignored)
chmod 600 ~/.ssh/<your-key>.pem
ssh -i ~/.ssh/<your-key>.pem ubuntu@<ip> true # accept host key once
```
Secrets come from environment variables, never files in the repo:
`GRAFANA_ADMIN_PASSWORD` (required, ≥ 8 chars), `DEPLOYGUARD_API_TOKEN` (optional; enables the `ci-cd` deployment record), `GHCR_USER` + `GHCR_TOKEN` (only for a private package; PAT needs `read:packages`).

## Run
```bash
ansible-playbook playbook.yml --syntax-check
ansible-playbook playbook.yml -e deployguard_image=ghcr.io/<owner>/<repo>:sha-<full-sha>
ansible-playbook playbook.yml -e deployguard_image=... --check    # dry run (limited: Docker steps are skipped-ish)
```
The play fails if the image is `latest`/not a `sha-` tag, the container never becomes healthy, `/health` or `/ready` fail, or Prometheus does not report the `deployguard` target `up`.

## Notes
Uses Ubuntu's `docker.io` and `docker-compose-v2` packages (no third-party apt keys). Tasks are idempotent; changing the image tag recreates only the app container. Validation status: `--syntax-check` and `ansible-lint` passed; a real run against EC2 has **not** been performed.
