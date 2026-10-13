# Terraform (optional AWS deployment)

Creates: one Ubuntu 24.04 EC2 instance (IMDSv2 only, encrypted gp3 root volume, public IPv4) and one security group (SSH from `ssh_allowed_cidr`; 8000/9090/3000 from `web_allowed_cidrs`). It uses the default VPC unless `vpc_id`/`subnet_id` are set. No IAM roles, keys or secrets are created or stored; the key pair must already exist.

## Commands
```bash
cp terraform.tfvars.example terraform.tfvars    # edit
terraform init
terraform fmt -check -recursive
terraform validate
terraform plan -out tf.plan
terraform apply tf.plan        # NOT run automatically anywhere in this project
terraform destroy              # cleanup
```

## IAM permissions for the operator (demo-scoped example; tighten with a region/tag condition if you can)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {"Effect": "Allow", "Action": [
      "ec2:RunInstances","ec2:TerminateInstances","ec2:DescribeInstances","ec2:DescribeInstanceTypes",
      "ec2:DescribeInstanceAttribute","ec2:DescribeInstanceCreditSpecifications","ec2:DescribeVolumes",
      "ec2:DescribeImages","ec2:DescribeVpcs","ec2:DescribeSubnets","ec2:DescribeKeyPairs",
      "ec2:DescribeSecurityGroups","ec2:DescribeSecurityGroupRules","ec2:DescribeNetworkInterfaces",
      "ec2:DescribeTags","ec2:DescribeAccountAttributes","ec2:CreateSecurityGroup","ec2:DeleteSecurityGroup",
      "ec2:AuthorizeSecurityGroupIngress","ec2:AuthorizeSecurityGroupEgress",
      "ec2:RevokeSecurityGroupIngress","ec2:RevokeSecurityGroupEgress","ec2:CreateTags","ec2:ModifyInstanceMetadataOptions"
    ], "Resource": "*"},
    {"Effect": "Allow", "Action": "ssm:GetParameter",
     "Resource": "arn:aws:ssm:*::parameter/aws/service/canonical/ubuntu/server/24.04/*"}
  ]
}
```
Permission lists can differ slightly by provider version; if `plan/apply` reports `UnauthorizedOperation`, add the named action.

**CI job user (separate, minimal):** only `ec2:AuthorizeSecurityGroupIngress`, `ec2:RevokeSecurityGroupIngress` (resource: your security-group ARN) and `ec2:DescribeSecurityGroups`.

## Cost
Billed while resources exist: EC2 instance hours, the EBS volume, and the public IPv4 address, plus data transfer. A `t3.small` is not normally free-tier eligible. Check the AWS Pricing Calculator for your region and set an AWS Budget alert. Stopping the instance still leaves EBS charges and changes the public IP; use `terraform destroy` to stop all charges, then verify in the console.

## Validation status
`tofu fmt -check` and an HCL parse passed in the build environment. `terraform validate/plan/apply` were **not** run (provider download and AWS credentials are required).
