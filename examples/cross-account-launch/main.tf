module "encryption_key" {
  source  = "registry.infrahouse.com/infrahouse/key/aws"
  version = "0.3.0"

  environment     = "production"
  service_name    = "golden-ami"
  key_name        = "golden-ami"
  key_description = "CMK used to encrypt golden AMIs shared cross-account"

  # The build account bakes and re-encrypts the AMI.
  key_users = [
    "arn:aws:iam::111111111111:role/image-builder"
  ]

  # Consumer accounts launch EC2/ASG from the shared, encrypted AMI. Account-root
  # ARNs let each consumer account create the AWS-resource grants EBS/Auto Scaling
  # require when launching from the CMK-encrypted, cross-account-shared AMI.
  key_launch_users = [
    "arn:aws:iam::222222222222:root", # sandbox
    "arn:aws:iam::333333333333:root", # development
    "arn:aws:iam::444444444444:root"  # production
  ]
}

output "kms_key_arn" {
  description = "The ARN of the created KMS key."
  value       = module.encryption_key.kms_key_arn
}
