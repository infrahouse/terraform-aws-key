module "test" {
  source          = "./../../"
  environment     = "development"
  service_name    = "key-test"
  key_name        = "test-key"
  key_description = "The key used for CI tests in infrahouse/terraform-aws-key"
  key_users       = var.key_users
}
