variable "region" {
  type = string
}
variable "role_arn" {
  type    = string
  default = null
}
variable "key_users" {
  type    = list(string)
  default = null
}
variable "key_encrypt_only_users" {
  type    = list(string)
  default = null
}
variable "key_decrypt_only_users" {
  type    = list(string)
  default = null
}
