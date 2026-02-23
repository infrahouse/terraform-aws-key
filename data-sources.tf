data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "key_policy" {
  statement {
    sid = "Enable IAM User Permissions"
    principals {
      identifiers = [
        "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
      ]
      type = "AWS"
    }
    actions   = ["kms:*"]
    resources = ["*"]
  }
  dynamic "statement" {
    for_each = try(length(var.key_users), 0) > 0 ? [1] : []
    content {
      sid = "Allow use of the key"
      principals {
        identifiers = var.key_users
        type        = "AWS"
      }
      actions = [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ]
      resources = ["*"]
    }
  }
  dynamic "statement" {
    for_each = try(length(var.key_encrypt_only_users), 0) > 0 ? [1] : []
    content {
      sid = "Allow encrypt only"
      principals {
        identifiers = var.key_encrypt_only_users
        type        = "AWS"
      }
      actions = [
        "kms:Encrypt",
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ]
      resources = ["*"]
    }
  }
  dynamic "statement" {
    for_each = try(length(var.key_decrypt_only_users), 0) > 0 ? [1] : []
    content {
      sid = "Allow decrypt only"
      principals {
        identifiers = var.key_decrypt_only_users
        type        = "AWS"
      }
      actions = [
        "kms:Decrypt",
        "kms:DescribeKey"
      ]
      resources = ["*"]
    }
  }
}
