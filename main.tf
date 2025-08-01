resource "aws_kms_key" "main" {
  description         = var.key_description
  enable_key_rotation = false
  tags = merge(
    local.default_module_tags,
    {
      module_version : local.module_version
    }
  )
  policy = data.aws_iam_policy_document.key_policy.json
}

resource "aws_kms_alias" "alias" {
  target_key_id = aws_kms_key.main.id
  name          = "alias/${var.key_name}"
}
