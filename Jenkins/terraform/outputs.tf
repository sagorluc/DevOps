# Output values from Terraform configuration

output "infrastructure_summary" {
  description = "Summary of provisioned infrastructure"
  value = {
    environment        = var.environment
    network_name      = docker_network.celery_network.name
    rabbitmq_name     = docker_container.rabbitmq.name
    rabbitmq_amqp_url = "amqp://guest:guest@${docker_container.rabbitmq.name}:5672/"
  }
}

output "connection_info" {
  description = "Connection information for services"
  value = {
    rabbitmq_management = "http://localhost:${var.rabbitmq_management_port}"
    rabbitmq_amqp_port  = var.rabbitmq_amqp_port
    web_port            = var.web_port
  }
}

output "network_id" {
  description = "Docker network ID"
  value       = docker_network.celery_network.id
  sensitive   = false
}

