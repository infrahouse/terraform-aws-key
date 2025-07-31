variable "environment" {
  description = "Environment name string."
  type        = string
}

variable "service_name" {
  description = "A descriptive name for the service that owns the queue."
  type        = string
}

variable "tags" {
  description = "A map of tags to add to resources."
  default     = {}
}
