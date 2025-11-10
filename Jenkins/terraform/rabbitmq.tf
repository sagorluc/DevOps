# RabbitMQ service configuration

resource "docker_image" "rabbitmq" {
  name = "rabbitmq:3-management"
  keep_locally = false
}

resource "docker_container" "rabbitmq" {
  image = docker_image.rabbitmq.image_id
  name  = "${local.name_prefix}-rabbitmq"
  
  ports {
    internal = 5672
    external = var.rabbitmq_amqp_port
  }
  
  ports {
    internal = 15672
    external = var.rabbitmq_management_port
  }
  
  networks_advanced {
    name = docker_network.celery_network.name
  }
  
  restart = "unless-stopped"
  
  labels {
    label = "service"
    value = "rabbitmq"
  }
  
  labels {
    label = "environment"
    value = var.environment
  }
  
  healthcheck {
    test     = ["CMD", "rabbitmq-diagnostics", "ping"]
    interval = "30s"
    timeout  = "10s"
    retries  = 3
    start_period = "40s"
  }
}

# Outputs
output "rabbitmq_container_name" {
  description = "Name of RabbitMQ container"
  value       = docker_container.rabbitmq.name
}

output "rabbitmq_amqp_url" {
  description = "RabbitMQ AMQP connection URL"
  value       = "amqp://guest:guest@${docker_container.rabbitmq.name}:5672/"
}

output "rabbitmq_management_url" {
  description = "RabbitMQ Management UI URL"
  value       = "http://localhost:${var.rabbitmq_management_port}"
}

