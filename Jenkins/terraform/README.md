# Terraform Infrastructure as Code

This directory contains Terraform configurations for provisioning infrastructure for the Django Celery Demo application.

## Overview

Terraform is used to define, provision, and manage infrastructure in a declarative way. This ensures:
- **Reproducibility**: Infrastructure can be recreated identically across environments
- **Version Control**: Infrastructure changes are tracked in Git
- **Consistency**: Same infrastructure configuration for dev, staging, and production
- **Automation**: Infrastructure provisioning can be automated in CI/CD pipelines

## Directory Structure

```
terraform/
├── main.tf              # Main configuration and provider setup
├── rabbitmq.tf         # RabbitMQ service definition
├── variables.tf         # Variable definitions
├── outputs.tf          # Output values
├── terraform.tfvars.example  # Example variables file
└── README.md           # This file
```

## Quick Start

1. **Copy example variables file:**
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars
   ```

2. **Edit variables:**
   ```bash
   nano terraform.tfvars  # Update with your values
   ```

3. **Initialize Terraform:**
   ```bash
   terraform init
   ```

4. **Plan changes:**
   ```bash
   terraform plan -var="environment=dev"
   ```

5. **Apply configuration:**
   ```bash
   terraform apply -var="environment=dev"
   ```

6. **Destroy infrastructure:**
   ```bash
   terraform destroy -var="environment=dev"
   ```

## Environment-Specific Deployments

### Development
```bash
terraform apply -var="environment=dev" -var="web_port=8000"
```

### Staging
```bash
terraform apply -var="environment=staging" -var="web_port=8080"
```

### Production
```bash
terraform apply -var="environment=production" -var="web_port=80"
```

## Integration with CI/CD

Terraform is integrated into the Jenkins pipeline:
- Infrastructure is provisioned before application deployment
- State is managed securely
- Changes are validated before applying

## State Management

For production, configure remote state backend in `main.tf`:
- AWS S3
- Azure Storage
- Google Cloud Storage
- HashiCorp Terraform Cloud

## Best Practices

1. **Never commit `.tfvars` files** with sensitive data
2. **Use remote state** for team collaboration
3. **Review plans** before applying
4. **Tag resources** for cost tracking
5. **Use workspaces** for environment separation

