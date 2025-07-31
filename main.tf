resource "aws_kms_key" "main" {
  enable_key_rotation = true
  tags = merge(
    local.default_module_tags,
    {
      module_version : local.module_version
    }
  )
}
