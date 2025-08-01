# terraform-aws-key

## Usage

```hcl
module "test" {
  source  = "infrahouse/key/aws"
  version = "0.1.0"

  environment     = "development"
  service_name    = "key-test"
  key_name        = "test-key"
  key_description = "The key used for CI tests in infrahouse/terraform-aws-key"
  key_users       = [
    "arn:aws:iam::303467602807:role/some-app-role"
  ]
}
```
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 5.62 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | ~> 5.62 |

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
| <a name="input_key_description"></a> [key\_description](#input\_key\_description) | A human readable description for the key. | `string` | n/a | yes |
| <a name="input_key_name"></a> [key\_name](#input\_key\_name) | A descriptive one word name for the key. Letters, digits, and \_-/ are allowed. | `string` | n/a | yes |
| <a name="input_key_users"></a> [key\_users](#input\_key\_users) | A list of IAM role ARNs that are allowed to use the key. | `list(string)` | `null` | no |
| <a name="input_service_name"></a> [service\_name](#input\_service\_name) | A descriptive name for the service that owns the queue. | `string` | n/a | yes |
| <a name="input_tags"></a> [tags](#input\_tags) | A map of tags to add to resources. | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_kms_key_arn"></a> [kms\_key\_arn](#output\_kms\_key\_arn) | n/a |
