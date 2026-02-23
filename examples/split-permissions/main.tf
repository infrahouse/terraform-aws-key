module "encryption_key" {
  source  = "registry.infrahouse.com/infrahouse/key/aws"
  version = "0.2.0"

  environment     = "production"
  service_name    = "data-pipeline"
  key_name        = "pipeline-data"
  key_description = "Encryption key for data pipeline"

  # Producer service can only encrypt
  key_encrypt_only_users = [
    "arn:aws:iam::123456789012:role/data-producer"
  ]

  # Consumer service can only decrypt
  key_decrypt_only_users = [
    "arn:aws:iam::123456789012:role/data-consumer"
  ]
}

output "kms_key_arn" {
  description = "The ARN of the created KMS key."
  value       = module.encryption_key.kms_key_arn
}
