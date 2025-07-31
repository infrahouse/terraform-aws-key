locals {
  module_version = "0.1.0"

  default_module_tags = merge(
    var.tags,
    {
      service : var.service_name
      created_by_module : "infrahouse/key/aws"
      environment : var.environment
    }
  )
}

