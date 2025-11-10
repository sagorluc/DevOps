# Variable definitions for Terraform configuration

variable "environment" {
  description = "Target environment (dev, staging, production)"
  type        = string
  
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be one of: dev, staging, production"
  }
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "celery-demo"
}

variable "docker_host" {
  description = "Docker daemon socket path or remote Docker host"
  type        = string
  default     = "unix:///var/run/docker.sock"
  sensitive   = false
}

variable "web_port" {
  description = "External port for web service"
  type        = number
  default     = 8000
}

variable "rabbitmq_amqp_port" {
  description = "External port for RabbitMQ AMQP protocol"
  type        = number
  default     = 5672
}

variable "rabbitmq_management_port" {
  description = "External port for RabbitMQ Management UI"
  type        = number
  default     = 15672
}

variable "enable_monitoring" {
  description = "Enable monitoring and logging services"
  type        = bool
  default     = false
}

variable "resource_tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}

