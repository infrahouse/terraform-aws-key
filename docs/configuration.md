# Configuration

## Required Variables

### `environment`

- **Type:** `string`
- **Description:** Environment name (e.g., `production`, `staging`, `development`).
  Used for resource tagging. Must be explicitly provided — no default.

### `service_name`

- **Type:** `string`
- **Description:** The name of the service that owns the key. Used for tagging.

### `key_name`

- **Type:** `string`
- **Description:** A descriptive name for the key, used as the KMS alias
  (`alias/{key_name}`). Must consist of letters, digits, underscores, hyphens,
  or slashes. Maximum 50 characters.

### `key_description`

- **Type:** `string`
- **Description:** A human-readable description stored with the KMS key in AWS.

## Optional Variables

### `key_users`

- **Type:** `list(string)`
- **Default:** `null`
- **Description:** IAM role ARNs granted full encrypt + decrypt access.
  When `null` or empty, no user access statement is added to the key policy.

### `key_encrypt_only_users`

- **Type:** `list(string)`
- **Default:** `null`
- **Description:** IAM role ARNs granted encrypt-only access
  (`kms:Encrypt`, `kms:ReEncryptTo`, `kms:GenerateDataKey*`, `kms:DescribeKey`).

!!! warning
    If a role appears in both `key_encrypt_only_users` and `key_decrypt_only_users`,
    it will effectively have full encrypt+decrypt access (equivalent to `key_users`).

### `key_decrypt_only_users`

- **Type:** `list(string)`
- **Default:** `null`
- **Description:** IAM role ARNs granted decrypt-only access
  (`kms:Decrypt`, `kms:DescribeKey`).

### `tags`

- **Type:** `map(string)`
- **Default:** `{}`
- **Description:** Additional tags to merge with the module's default tags.

## Outputs

### `kms_key_arn`

The ARN of the created KMS key. Use this to reference the key in other resources
(S3 encryption, EBS volumes, RDS instances, etc.).

## Example Configurations

### Minimal

```hcl
module "key" {
  source  = "registry.infrahouse.com/infrahouse/key/aws"
  version = "0.3.0"

  environment     = "production"
  service_name    = "my-app"
  key_name        = "my-app-data"
  key_description = "Encryption key for my-app"
}
```

No key users — only the root account can use the key.

### Full Access for a Single Role

```hcl
module "key" {
  source  = "registry.infrahouse.com/infrahouse/key/aws"
  version = "0.3.0"

  environment     = "production"
  service_name    = "my-app"
  key_name        = "my-app-data"
  key_description = "Encryption key for my-app"
  key_users       = ["arn:aws:iam::123456789012:role/my-app-role"]
}
```

### Split Permissions

```hcl
module "key" {
  source  = "registry.infrahouse.com/infrahouse/key/aws"
  version = "0.3.0"

  environment     = "production"
  service_name    = "my-app"
  key_name        = "my-app-data"
  key_description = "Encryption key for my-app"

  key_encrypt_only_users = ["arn:aws:iam::123456789012:role/writer"]
  key_decrypt_only_users = ["arn:aws:iam::123456789012:role/reader"]
}
```
