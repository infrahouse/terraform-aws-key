module "encryption_key" {
  source  = "registry.infrahouse.com/infrahouse/key/aws"
  version = "0.3.0"

  environment     = "production"
  service_name    = "my-app"
  key_name        = "my-app-data"
  key_description = "Encryption key for my-app data at rest"
  key_users = [
    "arn:aws:iam::123456789012:role/my-app-role"
  ]
}

output "kms_key_arn" {
  description = "The ARN of the created KMS key."
  value       = module.encryption_key.kms_key_arn
}
