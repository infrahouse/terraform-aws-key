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
        "kms:ReEncryptTo",
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
  # Launch users need to use the key directly (e.g. EC2/EBS DescribeKey) in
  # addition to creating grants, so these actions are granted unconditionally.
  dynamic "statement" {
    for_each = try(length(var.key_launch_users), 0) > 0 ? [1] : []
    content {
      sid = "Allow launch users to use the key"
      principals {
        identifiers = var.key_launch_users
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
  # CreateGrant is scoped with kms:GrantIsForAWSResource so it only applies when
  # an AWS service (EBS, Auto Scaling) creates the grant on the launcher's
  # behalf, not for arbitrary user-created grants. This is the pattern required
  # to launch EC2/ASG from a CMK-encrypted, cross-account-shared AMI.
  dynamic "statement" {
    for_each = try(length(var.key_launch_users), 0) > 0 ? [1] : []
    content {
      sid = "Allow launch users to create grants for AWS resources"
      principals {
        identifiers = var.key_launch_users
        type        = "AWS"
      }
      actions = [
        "kms:CreateGrant",
        "kms:ListGrants",
        "kms:RevokeGrant"
      ]
      resources = ["*"]
      condition {
        test     = "Bool"
        variable = "kms:GrantIsForAWSResource"
        values   = ["true"]
      }
    }
  }
}
