# Deployment guide

## A. Local (no cloud, no cost)
See README §10–11. This is the primary demonstration path.

## B. Optional AWS deployment (billable)
**Prereqs:** AWS account, IAM user for the demo (policy in `terraform/README.md`), an EC2 key pair in your region (`.pem` stays on your machine, `chmod 600`), Terraform, Ansible (Linux/macOS/WSL), AWS CLI configured.

1. **Provision**
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars   # set key_name, ssh_allowed_cidr, web_allowed_cidrs
   terraform init && terraform fmt -check && terraform validate
   terraform plan -out tf.plan
   terraform apply tf.plan          # only when you accept the cost
   terraform output
   ```
   Find your IP: `curl https://checkip.amazonaws.com` → use `x.x.x.x/32`.
2. **Get an image.** Push to `main` so Actions publishes `ghcr.io/<owner>/<repo>:sha-<commit>` (README §12). Copy the exact tag from the workflow summary/Packages page.
3. **Deploy by hand (recommended first run)**
   ```bash
   cd ../ansible
   cp inventory.ini.example inventory.ini     # public_ip + key path
   ansible-galaxy collection install -r requirements.yml
   export GRAFANA_ADMIN_PASSWORD='<min 8 chars>' DEPLOYGUARD_API_TOKEN="$(openssl rand -hex 16)"
   # private package only: export GHCR_USER=<github user> GHCR_TOKEN=<PAT with read:packages>
   ansible-playbook playbook.yml -e deployguard_image=ghcr.io/<owner>/<repo>:sha-<full-sha>
   ```
   First SSH connection asks to trust the host key; answer `yes` after checking the IP.
4. **Verify**
   ```bash
   curl -fsS http://<public_ip>:8000/health
   curl -fsS http://<public_ip>:8000/api/status
   ```
   Open `http://<public_ip>:3000` (Grafana) and `http://<public_ip>:9090/targets`.
5. **Automate:** configure variables/secrets (README §12) and push again; the `deploy` job needs approval on the `production` environment.
6. **Clean up:** `cd terraform && terraform destroy`; confirm in the console; delete demo IAM keys.

## What the playbook does (idempotent)
ping → assert inputs → install `docker.io`, `docker-compose-v2` → create `/opt/deployguard` → copy monitoring + prod compose → write `.env` (0600) → optional GHCR login → `compose pull + up` → wait for container health → `/health`, `/ready` → Prometheus target `up` → optional deployment record. Any failed step fails the run.

## Rollback
Re-run the playbook with the previous known-good `sha-` tag. Data volumes are preserved.
