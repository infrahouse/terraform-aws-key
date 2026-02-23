# Getting Started

## Prerequisites

- [Terraform](https://www.terraform.io/downloads) >= 1.5
- AWS provider >= 5.62, < 7.0
- An AWS account with permissions to create KMS keys
- IAM role ARNs for any principals that need key access

## First Deployment

### 1. Add the module to your Terraform configuration

```hcl
module "encryption_key" {
  source  = "registry.infrahouse.com/infrahouse/key/aws"
  version = "0.3.0"

  environment     = "production"
  service_name    = "my-app"
  key_name        = "my-app-data"
  key_description = "Encryption key for my-app data at rest"
  key_users       = [
    "arn:aws:iam::123456789012:role/my-app-role"
  ]
}
```

### 2. Initialize and apply

```bash
terraform init
terraform plan
terraform apply
```

### 3. Use the key ARN

The module outputs `kms_key_arn` which you can reference in other resources:

```hcl
resource "aws_s3_bucket_server_side_encryption_configuration" "example" {
  bucket = aws_s3_bucket.example.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = module.encryption_key.kms_key_arn
    }
  }
}
```

## IAM Permissions

The caller creating the KMS key needs the following IAM permissions:

- `kms:CreateKey`
- `kms:CreateAlias`
- `kms:DeleteAlias`
- `kms:UpdateAlias`
- `kms:TagResource`
- `kms:PutKeyPolicy`
- `kms:DescribeKey`
- `kms:GetKeyPolicy`
- `kms:ListResourceTags`
- `kms:ScheduleKeyDeletion` (for destroy)

The root account of the AWS account always retains full `kms:*` access to the key
via the key policy, ensuring you can never lock yourself out.
