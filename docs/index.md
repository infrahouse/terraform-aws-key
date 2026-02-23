# terraform-aws-key

An InfraHouse Terraform module that creates an AWS KMS key with an alias and configurable
key policy. Published to the Terraform Registry as
[infrahouse/key/aws](https://registry.terraform.io/modules/infrahouse/key/aws/latest).

## Features

- Creates a KMS symmetric encryption key with automatic annual key rotation
- Creates a KMS alias for human-readable references
- Configurable key policy granting encrypt and/or decrypt permissions to IAM roles
- Split permissions: grant encrypt-only or decrypt-only access to different roles
- Root account always retains full key management access
- Standard InfraHouse resource tagging
- Supports AWS provider versions 5 and 6

## Quick Start

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

## Next Steps

- [Getting Started](getting-started.md) — prerequisites and first deployment
- [Configuration](configuration.md) — all variables explained
- [Architecture](architecture.md) — how the module works
- [Examples](examples.md) — common use cases
