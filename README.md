# terraform-aws-key

[![Need Help?](https://img.shields.io/badge/Need%20Help%3F-Contact%20Us-0066CC)](https://infrahouse.com/contact)
[![Docs](https://img.shields.io/badge/docs-github.io-blue)](https://infrahouse.github.io/terraform-aws-key/)
[![Registry](https://img.shields.io/badge/Terraform-Registry-purple?logo=terraform)](https://registry.terraform.io/modules/infrahouse/key/aws/latest)
[![Release](https://img.shields.io/github/release/infrahouse/terraform-aws-key.svg)](https://github.com/infrahouse/terraform-aws-key/releases/latest)
[![AWS KMS](https://img.shields.io/badge/AWS-KMS-orange?logo=amazonwebservices)](https://aws.amazon.com/kms/)
[![Security](https://img.shields.io/github/actions/workflow/status/infrahouse/terraform-aws-key/vuln-scanner-pr.yml?label=Security)](https://github.com/infrahouse/terraform-aws-key/actions/workflows/vuln-scanner-pr.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

## Why This Module?

AWS KMS key management involves creating the key, setting up an alias, configuring a key policy,
and enabling automatic rotation. This module wraps all of that into a single resource with
a clean interface for granting encrypt and/or decrypt permissions to IAM roles.

It also supports **split permissions** — granting encrypt-only or decrypt-only access to
different roles — which is essential for least-privilege architectures where producers
write encrypted data and consumers read it, without either having both capabilities.

## Features

- Creates a KMS key with automatic annual key rotation enabled
- Creates a KMS alias for human-readable key references
- Configurable key policy via IAM role ARN lists
- Split encrypt/decrypt permissions (`key_encrypt_only_users`, `key_decrypt_only_users`)
- Full encrypt+decrypt access via `key_users`
- Root account retains full key management access
- Supports AWS provider versions 5 and 6
- Standard InfraHouse tagging (environment, service, created_by_module, module_version)

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

### Envelope Encryption Example

```python
import boto3

kms = boto3.client("kms")
key_arn = "arn:aws:kms:us-west-2:123456789012:key/..."

# Encrypt
response = kms.encrypt(KeyId=key_arn, Plaintext=b"Hello world")
ciphertext = response["CiphertextBlob"]

# Decrypt
response = kms.decrypt(CiphertextBlob=ciphertext)
plaintext = response["Plaintext"]  # b"Hello world"
```

## Documentation

Full documentation is available at
[infrahouse.github.io/terraform-aws-key](https://infrahouse.github.io/terraform-aws-key/).

- [Getting Started](https://infrahouse.github.io/terraform-aws-key/getting-started/)
- [Configuration](https://infrahouse.github.io/terraform-aws-key/configuration/)
- [Architecture](https://infrahouse.github.io/terraform-aws-key/architecture/)
- [Examples](https://infrahouse.github.io/terraform-aws-key/examples/)
- [Troubleshooting](https://infrahouse.github.io/terraform-aws-key/troubleshooting/)

<!-- BEGIN_TF_DOCS -->

## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 5.62, < 7.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 5.62, < 7.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_kms_alias.alias](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_alias) | resource |
| [aws_kms_key.main](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key) | resource |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |
| [aws_iam_policy_document.key_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_environment"></a> [environment](#input\_environment) | Environment name string. | `string` | n/a | yes |
| <a name="input_key_decrypt_only_users"></a> [key\_decrypt\_only\_users](#input\_key\_decrypt\_only\_users) | A list of IAM role ARNs that are allowed to decrypt with the key but not encrypt.<br/>If a role appears in both this list and key\_encrypt\_only\_users, it will effectively<br/>have full encrypt+decrypt access (equivalent to key\_users). | `list(string)` | `null` | no |
| <a name="input_key_description"></a> [key\_description](#input\_key\_description) | A human readable description for the key. | `string` | n/a | yes |
| <a name="input_key_encrypt_only_users"></a> [key\_encrypt\_only\_users](#input\_key\_encrypt\_only\_users) | A list of IAM role ARNs that are allowed to encrypt with the key but not decrypt.<br/>If a role appears in both this list and key\_decrypt\_only\_users, it will effectively<br/>have full encrypt+decrypt access (equivalent to key\_users). | `list(string)` | `null` | no |
| <a name="input_key_name"></a> [key\_name](#input\_key\_name) | A descriptive one word name for the key. Letters, digits, and \_-/ are allowed. | `string` | n/a | yes |
| <a name="input_key_users"></a> [key\_users](#input\_key\_users) | A list of IAM role ARNs that are allowed to use the key for both encrypt and decrypt. | `list(string)` | `null` | no |
| <a name="input_service_name"></a> [service\_name](#input\_service\_name) | A descriptive name for the service that owns the key. | `string` | n/a | yes |
| <a name="input_tags"></a> [tags](#input\_tags) | A map of tags to add to resources. | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_kms_key_arn"></a> [kms\_key\_arn](#output\_kms\_key\_arn) | The Amazon Resource Name (ARN) of the KMS key created by this module. |
<!-- END_TF_DOCS -->

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[Apache 2.0](LICENSE)
