# Credentials are NOT configured here. Use `aws configure`, AWS_PROFILE or
# AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY environment variables.
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project   = "deployguard"
      ManagedBy = "terraform"
    }
  }
}
