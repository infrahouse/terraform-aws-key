output "kms_key_arn" {
  description = "The Amazon Resource Name (ARN) of the KMS key created by this module."
  value       = aws_kms_key.main.arn
}
