variable "aws_region" {
  description = "AWS region for the demo (choose one close to you)."
  type        = string
  default     = "ap-south-1"
}

variable "instance_type" {
  description = "EC2 instance type. t3.small (2 GB RAM) is the smallest comfortable size for app + Prometheus + Grafana."
  type        = string
  default     = "t3.small"
}

variable "key_name" {
  description = "Name of an EXISTING EC2 key pair in the region. The private key stays on your machine."
  type        = string
}

variable "ssh_allowed_cidr" {
  description = "Trusted CIDR allowed to SSH, e.g. your public IP as x.x.x.x/32. 0.0.0.0/0 is rejected."
  type        = string

  validation {
    condition     = can(cidrhost(var.ssh_allowed_cidr, 0)) && var.ssh_allowed_cidr != "0.0.0.0/0" && var.ssh_allowed_cidr != "::/0"
    error_message = "ssh_allowed_cidr must be a valid CIDR and must not be 0.0.0.0/0."
  }
}

variable "web_allowed_cidrs" {
  description = "CIDRs allowed to reach the app (8000), Prometheus (9090) and Grafana (3000). Keep this to your own IP."
  type        = list(string)

  validation {
    condition     = length(var.web_allowed_cidrs) > 0 && alltrue([for c in var.web_allowed_cidrs : can(cidrhost(c, 0))])
    error_message = "Provide at least one valid CIDR."
  }
}

variable "vpc_id" {
  description = "VPC to use. null = the region's default VPC."
  type        = string
  default     = null
}

variable "subnet_id" {
  description = "Public subnet to use. null = first subnet of the selected VPC."
  type        = string
  default     = null
}

variable "root_volume_gb" {
  description = "Root EBS volume size (gp3, encrypted)."
  type        = number
  default     = 20
}

variable "name_prefix" {
  description = "Prefix for resource names."
  type        = string
  default     = "deployguard"
}
