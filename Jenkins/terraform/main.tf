# Main Terraform configuration for Django Celery Demo Infrastructure
# This file defines the core infrastructure components

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
    # Uncomment and configure for cloud providers
    # aws = {
    #   source  = "hashicorp/aws"
    #   version = "~> 5.0"
    # }
  }
  
  # Backend configuration for state management
  # Uncomment and configure based on your backend choice
  # backend "s3" {
  #   bucket = "your-terraform-state-bucket"
  #   key    = "celery-demo/terraform.tfstate"
  #   region = "us-east-1"
  # }
  
  # Alternative: Local backend (for development)
  backend "local" {
    path = "terraform.tfstate"
  }
}

# Provider configuration
provider "docker" {
  host = var.docker_host
}

# Variables
variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "celery-demo"
}

variable "docker_host" {
  description = "Docker daemon socket path"
  type        = string
  default     = "unix:///var/run/docker.sock"
}

variable "web_port" {
  description = "Port for web service"
  type        = number
  default     = 8000
}

variable "rabbitmq_management_port" {
  description = "Port for RabbitMQ management UI"
  type        = number
  default     = 15672
}

variable "rabbitmq_amqp_port" {
  description = "Port for RabbitMQ AMQP"
  type        = number
  default     = 5672
}

# Local values for computed resources
locals {
  environment = var.environment
  name_prefix = "${var.project_name}-${var.environment}"
  
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Docker network for services
resource "docker_network" "celery_network" {
  name = "${local.name_prefix}-network"
  
  driver = "bridge"
  
  ipam_config {
    subnet = "172.20.0.0/16"
  }
  
  labels {
    label = "environment"
    value = var.environment
  }
  
  labels {
    label = "project"
    value = var.project_name
  }
}

# Outputs
output "network_name" {
  description = "Name of the Docker network"
  value       = docker_network.celery_network.name
}

output "network_id" {
  description = "ID of the Docker network"
  value       = docker_network.celery_network.id
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}

