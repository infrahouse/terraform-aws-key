# Examples

## Basic KMS Key

A minimal KMS key with full encrypt/decrypt access for a single IAM role.

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

See [`examples/basic/`](https://github.com/infrahouse/terraform-aws-key/tree/main/examples/basic)
for a complete working example.

## Split Encrypt/Decrypt Permissions

Grant encrypt-only access to a producer service and decrypt-only access to a consumer,
following the principle of least privilege.

```hcl
module "encryption_key" {
  source  = "registry.infrahouse.com/infrahouse/key/aws"
  version = "0.3.0"

  environment     = "production"
  service_name    = "data-pipeline"
  key_name        = "pipeline-data"
  key_description = "Encryption key for data pipeline"

  key_encrypt_only_users = [
    "arn:aws:iam::123456789012:role/data-producer"
  ]
  key_decrypt_only_users = [
    "arn:aws:iam::123456789012:role/data-consumer"
  ]
}
```

See
[`examples/split-permissions/`](https://github.com/infrahouse/terraform-aws-key/tree/main/examples/split-permissions)
for a complete working example.

## S3 Bucket Encryption

Use the KMS key to encrypt an S3 bucket:

```hcl
module "encryption_key" {
  source  = "registry.infrahouse.com/infrahouse/key/aws"
  version = "0.3.0"

  environment     = "production"
  service_name    = "my-app"
  key_name        = "s3-data"
  key_description = "Encryption key for S3 bucket data"
  key_users       = [
    "arn:aws:iam::123456789012:role/my-app-role"
  ]
}

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

## Multiple Roles with Mixed Permissions

Combine all three user lists for complex access patterns:

```hcl
module "encryption_key" {
  source  = "registry.infrahouse.com/infrahouse/key/aws"
  version = "0.3.0"

  environment     = "production"
  service_name    = "shared-data"
  key_name        = "shared-data"
  key_description = "Shared encryption key with role-based access"

  # Admin role gets full access
  key_users = [
    "arn:aws:iam::123456789012:role/admin"
  ]

  # API services can only encrypt (write)
  key_encrypt_only_users = [
    "arn:aws:iam::123456789012:role/api-service-a",
    "arn:aws:iam::123456789012:role/api-service-b"
  ]

  # Backend processors can only decrypt (read)
  key_decrypt_only_users = [
    "arn:aws:iam::123456789012:role/processor"
  ]
}
```

## Using the Key in Python

### Simple Encrypt/Decrypt

The simplest way to use a KMS key — encrypt and decrypt small payloads (up to 4 KB)
directly via the KMS API:

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

### Envelope Encryption with Fernet

For data larger than 4 KB, use
[envelope encryption](https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html#enveloping):
KMS generates a data key, you encrypt data locally with that key, then store the
encrypted data key alongside the ciphertext. This way, KMS only encrypts/decrypts the
small data key, not your entire payload.

This example uses [Fernet](https://cryptography.io/en/latest/fernet/) from the
`cryptography` library (AES-128-CBC with HMAC authentication):

```python
import base64
import boto3
from cryptography.fernet import Fernet

kms = boto3.client("kms")
key_arn = "arn:aws:kms:us-west-2:123456789012:key/..."

# --- Encrypt ---

# Ask KMS for a data key (plaintext + encrypted copies)
response = kms.generate_data_key(KeyId=key_arn, KeySpec="AES_256")
plaintext_key = response["Plaintext"]       # 32 bytes, use locally
encrypted_key = response["CiphertextBlob"]  # store this, it's safe

# Encrypt your data locally with the plaintext key
# Fernet expects a 32-byte key, base64url-encoded
fernet = Fernet(base64.urlsafe_b64encode(plaintext_key))
ciphertext = fernet.encrypt(b"This can be megabytes of data")

# Discard the plaintext key from memory
del plaintext_key

# Store encrypted_key + ciphertext together (e.g., in S3 or a database)
# encrypted_key is ~200 bytes; ciphertext is your data + overhead

# --- Decrypt ---

# Recover the plaintext data key via KMS
response = kms.decrypt(CiphertextBlob=encrypted_key)
plaintext_key = response["Plaintext"]

# Decrypt the data locally
fernet = Fernet(base64.urlsafe_b64encode(plaintext_key))
data = fernet.decrypt(ciphertext)  # b"This can be megabytes of data"
```

!!! tip
    Install with `pip install cryptography`. Fernet provides authenticated encryption
    (AES-CBC + HMAC-SHA256), so it detects tampering automatically.
