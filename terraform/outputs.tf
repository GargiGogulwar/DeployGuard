output "instance_id" {
  description = "EC2 instance ID."
  value       = aws_instance.deployguard.id
}

output "public_ip" {
  description = "Public IP (use as ansible_host / EC2_HOST). Changes if the instance is stopped and started."
  value       = aws_instance.deployguard.public_ip
}

output "security_group_id" {
  description = "Security group ID (needed by the optional CI job that temporarily opens SSH for the runner)."
  value       = aws_security_group.deployguard.id
}

output "app_url" {
  value = "http://${aws_instance.deployguard.public_ip}:8000"
}

output "grafana_url" {
  value = "http://${aws_instance.deployguard.public_ip}:3000"
}

output "prometheus_url" {
  value = "http://${aws_instance.deployguard.public_ip}:9090"
}

output "ssh_command" {
  value = "ssh -i <path-to-your-private-key> ubuntu@${aws_instance.deployguard.public_ip}"
}
