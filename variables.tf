variable "environment" {
  description = "Environment name string."
  type        = string
}

variable "key_description" {
  description = "A human readable description for the key."
  type        = string
}

variable "key_name" {
  description = "A descriptive one word name for the key. Letters, digits, and _-/ are allowed."
  type        = string
  validation {
    condition     = can(regex("^[a-zA-Z0-9-_/]+$", var.key_name)) && length(var.key_name) <= 50
    error_message = "The key_name must consist of letters, digits, underscores, hyphens, or slashes and must not exceed 50 characters."
  }
}

variable "key_users" {
  description = "A list of IAM role ARNs that are allowed to use the key for both encrypt and decrypt."
  type        = list(string)
  default     = null
}

variable "key_encrypt_only_users" {
  description = <<-EOT
    A list of IAM role ARNs that are allowed to encrypt with the key but not decrypt.
    If a role appears in both this list and key_decrypt_only_users, it will effectively
    have full encrypt+decrypt access (equivalent to key_users).
  EOT
  type        = list(string)
  default     = null
}

variable "key_decrypt_only_users" {
  description = <<-EOT
    A list of IAM role ARNs that are allowed to decrypt with the key but not encrypt.
    If a role appears in both this list and key_encrypt_only_users, it will effectively
    have full encrypt+decrypt access (equivalent to key_users).
  EOT
  type        = list(string)
  default     = null
}

variable "service_name" {
  description = "A descriptive name for the service that owns the key."
  type        = string
}

variable "tags" {
  description = "A map of tags to add to resources."
  type        = map(string)
  default     = {}
}
