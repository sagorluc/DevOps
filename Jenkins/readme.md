# Django Celery Demo Project with Jenkins CI/CD Pipeline

A production-ready Django application with Celery task queue integration, featuring a complete CI/CD pipeline using Jenkins that supports multi-environment deployments (dev, staging, production) with automated Slack notifications.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Key Files Explained](#key-files-explained)
  - [docker-compose.yml](#1-docker-composeyml---local-development-orchestration)
  - [docker-compose.deploy.yml](#2-cidocker-compose-deployyml---production-deployment-configuration)
  - [deploy.sh](#3-cideploysh---automated-deployment-script)
  - [Jenkinsfile](#4-jenkinsfile---main-cicd-pipeline-definition)
  - [Jenkinsfile.staging](#5-jenkinsfilestaging---legacysimple-staging-pipeline)
  - [Terraform Configuration](#6-terraform-infrastructure-as-code)
  - [How These Files Work Together](#how-these-files-work-together)
- [Step-by-Step Setup Guide](#step-by-step-setup-guide)
- [Local Development](#local-development)
- [Docker Setup](#docker-setup)
- [Terraform Infrastructure Setup](#terraform-infrastructure-setup)
- [CI/CD Pipeline Configuration](#cicd-pipeline-configuration)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## 🎯 Project Overview

This project demonstrates:

- **Django REST Framework** application with JWT authentication
- **Celery** for asynchronous task processing
- **RabbitMQ** as the message broker
- **Docker** containerization with multi-service orchestration
- **Terraform** for Infrastructure as Code (IaC) provisioning
- **GitHub Actions** for Continuous Integration (CI) on dev branch
- **Jenkins CI/CD** pipeline for Continuous Deployment (CD)
- **Multi-environment** support (dev, staging, production)
- **Git branching strategy**: main = production, dev = staging
- **Slack integration** for deployment notifications

### Key Features

- Restaurant and seller profile management
- Temporary role assignments with automatic expiration
- Scheduled Celery tasks (periodic cleanup, cache clearing)
- Production-ready settings with environment-based configuration
- Automated database migrations
- Health checks and monitoring

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

1. **Python 3.9+**
   ```bash
   python3 --version
   ```

2. **Docker & Docker Compose**
   ```bash
   docker --version
   docker compose version
   ```

3. **Git**
   ```bash
   git --version
   ```

4. **Terraform** (for Infrastructure as Code)
   ```bash
   terraform --version
   ```
   - Terraform 1.0+ required
   - Install from: https://www.terraform.io/downloads

5. **Jenkins** (for CI/CD)
   - Jenkins 2.400+ with Pipeline plugin
   - Docker plugin
   - Slack Notification plugin

### Optional (for local development)

- **PostgreSQL** (for production-like database)
- **Redis** (alternative to RabbitMQ)

## 📁 Project Structure

```
.
├── celery_app/              # Main Django application
│   ├── models.py           # Restaurant, SellerProfile, TemporaryRole models
│   ├── views.py            # API views
│   ├── serializers.py      # DRF serializers
│   ├── urls.py             # URL routing
│   └── migrations/         # Database migrations
├── celery_demo/            # Django project settings
│   ├── settings.py         # Main settings (environment-aware)
│   ├── celery.py           # Celery configuration
│   ├── tasks.py            # Celery task definitions
│   ├── urls.py             # Root URL configuration
│   └── wsgi.py             # WSGI application
├── ci/                     # CI/CD scripts
│   ├── deploy.sh           # Deployment automation script
│   ├── terraform.sh        # Terraform automation script
│   └── docker-compose.deploy.yml  # Production compose file
├── terraform/              # Infrastructure as Code
│   ├── main.tf             # Main Terraform configuration
│   ├── rabbitmq.tf        # RabbitMQ infrastructure
│   ├── variables.tf       # Variable definitions
│   ├── outputs.tf         # Output values
│   └── terraform.tfvars.example  # Example variables
├── deployments/            # Environment configuration files
│   ├── dev.env             # Development environment variables
│   ├── staging.env         # Staging environment variables
│   └── production.env      # Production environment variables
├── docs/                   # Documentation
│   ├── CI_CD.md           # CI/CD pipeline documentation
│   └── PIPELINE_EXPLANATION.md  # Line-by-line pipeline explanations
├── .github/                # GitHub Actions workflows
│   └── workflows/
│       └── ci.yml         # CI pipeline (runs on dev branch merge)
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Local development compose file
├── Jenkinsfile             # Jenkins pipeline definition
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 📚 Key Files Explained

This section provides detailed explanations of the critical configuration files used in this project, their purposes, and why they're structured the way they are.

### 1. `docker-compose.yml` - Local Development Orchestration

**Location:** Root directory  
**Purpose:** Defines the multi-container setup for local development and testing

**Why We Use It:**
- **Simplifies Development:** Instead of manually starting RabbitMQ, Django server, and Celery worker separately, Docker Compose orchestrates all services with a single command
- **Consistent Environment:** Ensures all developers work with the same service versions and configurations
- **Service Dependencies:** Automatically handles service startup order (RabbitMQ must start before Celery)
- **Network Isolation:** Creates a dedicated Docker network so services can communicate securely

**Key Features:**
```yaml
# Builds the image from local Dockerfile (for development)
build:
  context: .

# Uses environment-specific .env files
env_file:
  - ${ENV_FILE:-deployments/dev.env}

# Development server command (not production-ready)
command: python manage.py runserver 0.0.0.0:8001
```

**When to Use:**
- Local development on your machine
- Testing changes before committing
- Running the full stack without Jenkins
- Quick prototyping and debugging

**Example Usage:**
```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down
```

---

### 2. `ci/docker-compose.deploy.yml` - Production Deployment Configuration

**Location:** `ci/` directory  
**Purpose:** Production-ready Docker Compose configuration for automated deployments

**Why We Use It (Different from `docker-compose.yml`):**
- **Pre-built Images:** Uses pre-built images from a registry instead of building locally
  ```yaml
  image: ${APP_IMAGE:?APP_IMAGE is required}  # Must be provided
  # No 'build:' section - image already exists
  ```
- **Production Server:** Uses Gunicorn (production WSGI server) instead of Django's development server
  ```yaml
  command: gunicorn celery_demo.wsgi:application --bind 0.0.0.0:8000
  ```
- **Strict Requirements:** Fails fast if required environment variables are missing
  ```yaml
  ${APP_IMAGE:?APP_IMAGE is required}  # Error if not set
  ```
- **Deployment Safety:** Designed for CI/CD pipelines where images are already built and tested

**Key Differences from `docker-compose.yml`:**

| Feature | docker-compose.yml | docker-compose.deploy.yml |
|---------|-------------------|---------------------------|
| Image Source | Builds from Dockerfile | Uses pre-built image |
| Web Server | Django dev server | Gunicorn (production) |
| Use Case | Local development | Production deployment |
| Environment | Flexible defaults | Strict requirements |

**When to Use:**
- Automated deployments via Jenkins
- Production/staging environment rollouts
- When you have a pre-built Docker image in a registry
- Zero-downtime deployments with proper orchestration

**Example Usage:**
```bash
# Deployed via deploy.sh script
./ci/deploy.sh production registry.example.com/celery-demo:v1.2.3
```

---

### 3. `ci/deploy.sh` - Automated Deployment Script

**Location:** `ci/` directory  
**Purpose:** Standardized deployment automation script that handles environment-specific deployments

**Why We Use It:**
- **Consistency:** Ensures every deployment follows the same steps (pull → migrate → deploy)
- **Error Handling:** Uses `set -Eeuo pipefail` to fail immediately on any error, preventing partial deployments
- **Environment Abstraction:** Automatically loads the correct `.env` file based on environment name
- **Docker Context Support:** Can deploy to remote Docker hosts (useful for production servers)
- **Migration Safety:** Runs database migrations before starting new containers

**How It Works:**
```bash
#!/usr/bin/env bash
set -Eeuo pipefail  # Exit on error, undefined vars, pipe failures

# 1. Validates inputs
ENVIRONMENT="$1"      # dev, staging, or production
IMAGE_TAG="$2"        # Pre-built image from registry
COMPOSE_FILE="${3:-ci/docker-compose.deploy.yml}"

# 2. Loads environment-specific configuration
ENV_FILE="deployments/${ENVIRONMENT}.env"

# 3. Supports remote Docker contexts (optional)
DOCKER_CONTEXT="${!CONTEXT_VAR_NAME:-}"  # For remote deployments

# 4. Executes deployment steps:
#    - Pull latest image
#    - Run database migrations
#    - Start/update services
#    - Show service status
```

**Deployment Flow:**
1. **Pull Image:** Downloads the latest image from registry
   ```bash
   compose pull
   ```
2. **Run Migrations:** Applies database schema changes safely
   ```bash
   compose run --rm web python manage.py migrate --noinput
   ```
3. **Deploy Services:** Starts/updates all containers
   ```bash
   compose up -d --remove-orphans
   ```
4. **Verify Status:** Shows running containers
   ```bash
   compose ps
   ```

**Why This Approach:**
- **Idempotent:** Can run multiple times safely (won't break if already deployed)
- **Zero-Downtime Ready:** With proper health checks, can support rolling updates
- **Auditable:** Each deployment step is logged and visible
- **Flexible:** Works with local Docker or remote Docker contexts

**Example Usage:**
```bash
# Deploy to development
./ci/deploy.sh dev registry.example.com/celery-demo:dev-abc123

# Deploy to staging
./ci/deploy.sh staging registry.example.com/celery-demo:staging-xyz789

# Deploy to production
./ci/deploy.sh production registry.example.com/celery-demo:v1.2.3
```

---

### 4. `Jenkinsfile` - Main CI/CD Pipeline Definition

**Location:** Root directory  
**Purpose:** Defines the complete CI/CD pipeline with multi-environment support and Slack notifications

**Why We Use It:**
- **Automation:** Eliminates manual deployment steps, reducing human error
- **Standardization:** Every deployment follows the exact same process
- **Visibility:** Slack notifications keep the team informed of deployment status
- **Testing:** Automatically runs tests before deployment
- **Versioning:** Creates unique image tags based on commit hash and build number
- **Multi-Environment:** Single pipeline handles dev, staging, and production with parameter selection

**Pipeline Stages Explained:**

1. **Preparation**
   - Cleans workspace to ensure a fresh start
   - Prevents contamination from previous builds

2. **Checkout**
   - Retrieves source code from Git repository
   - Ensures Jenkins works with the correct code version

3. **Set Up Python**
   - Creates isolated virtual environment
   - Upgrades pip and wheel for dependency installation

4. **Install Dependencies**
   - Installs all Python packages from `requirements.txt`
   - Ensures build environment matches production

5. **Static Analysis**
   - Syntax checking with `compileall`
   - Catches basic Python errors before runtime

6. **Run Tests** (Optional)
   - Executes Django test suite
   - Can be skipped for faster deployments if needed

7. **Prepare Build Metadata**
   - Generates unique image tag: `{env}-{commit}-{build}`
   - Example: `production-a1b2c3d-42`
   - Ensures traceability of deployed versions

8. **Build Docker Image**
   - Builds application image with environment-specific build args
   - Tags image with generated tag

9. **Publish Docker Image**
   - Pushes image to Docker registry
   - Makes image available for deployment

10. **Deploy** (Environment-Specific)
    - Calls `deploy.sh` with appropriate environment
    - Only runs for the selected environment parameter

**Key Features:**

```groovy
// Slack notifications at every stage
def notifySlack(String stageName, String status, String customMessage = null)

// Environment selection via parameter
parameters {
    choice(name: 'DEPLOY_ENV', choices: ['dev', 'staging', 'production'])
}

// Conditional deployment stages
stage('Deploy Production') {
    when {
        expression { params.DEPLOY_ENV == 'production' }
    }
}
```

**Why This Structure:**
- **Separation of Concerns:** Each stage has a single responsibility
- **Failure Handling:** Pipeline stops on failure, preventing bad deployments
- **Notification Integration:** Team always knows deployment status
- **Flexibility:** Parameters allow customization per build
- **Best Practices:** Follows Jenkins Pipeline best practices

**Example Workflow:**
1. Developer pushes code to repository
2. Jenkins detects change and triggers pipeline
3. User selects environment (dev/staging/production) and clicks Build
4. Pipeline runs all stages automatically
5. Slack notifications sent at each stage
6. Application deployed to selected environment

---

### 5. `Jenkinsfile.staging` - Legacy/Simple Staging Pipeline

**Location:** Root directory  
**Purpose:** A simpler, environment-specific pipeline for staging deployments (legacy/alternative approach)

**Why It Exists:**
- **Simpler Alternative:** Less complex than the main `Jenkinsfile`
- **Environment-Specific:** Hardcoded for staging environment only
- **Learning Tool:** Shows a basic pipeline structure without multi-environment complexity
- **Quick Deployments:** Faster to understand and modify for simple use cases

**Key Differences from Main `Jenkinsfile`:**

| Feature | Jenkinsfile | Jenkinsfile.staging |
|---------|-------------|---------------------|
| Environments | Multi (dev/staging/prod) | Single (staging only) |
| Parameters | Yes (selectable) | No (hardcoded) |
| Slack Notifications | Yes (comprehensive) | No |
| Image Tagging | Dynamic (commit+build) | Static name |
| Registry Push | Yes | No (local only) |
| Deployment Script | Uses `deploy.sh` | Manual Docker commands |

**Structure:**
```groovy
pipeline {
    stages {
        stage('Test Docker') { ... }           # Verify Docker works
        stage('Build Docker Image') { ... }    # Build image
        stage('Run RabbitMQ Service') { ... }  # Start RabbitMQ
        stage('Run Application') { ... }       # Start Django
        stage('Run Celery Worker') { ... }     # Start Celery
    }
}
```

**When to Use:**
- Simple staging deployments without full CI/CD requirements
- Learning Jenkins pipelines (simpler example)
- Quick local testing of Jenkins setup
- When you don't need multi-environment support

**Limitations:**
- No image versioning or registry integration
- No automated testing
- No Slack notifications
- Manual container management (not using docker-compose)
- Harder to maintain (duplicate code if you need multiple environments)

**Recommendation:**
- Use the main `Jenkinsfile` for production deployments
- Use `Jenkinsfile.staging` only for simple staging or as a learning reference
- Consider removing it once the main pipeline is working

---

### 6. `Terraform` - Infrastructure as Code (IaC)

**Location:** `terraform/` directory  
**Purpose:** Define, provision, and manage infrastructure in a declarative, version-controlled way

**Why We Need Terraform:**

#### 🎯 The Problem Without Terraform

**Manual Infrastructure Management:**
- ❌ Infrastructure created manually through web consoles or CLI commands
- ❌ No record of what was created or how
- ❌ Difficult to recreate environments identically
- ❌ Configuration drift between environments
- ❌ Time-consuming manual setup for each environment
- ❌ No way to version control infrastructure changes
- ❌ Hard to rollback infrastructure changes
- ❌ Difficult to audit what infrastructure exists

**Example Without Terraform:**
```bash
# Manual steps (error-prone, not reproducible)
docker network create celery_network
docker run -d --name rabbitmq --network celery_network ...
docker run -d --name web --network celery_network ...
# What if you need to recreate this? What if ports conflict?
# What if you forget a step? No documentation!
```

#### ✅ The Solution With Terraform

**Infrastructure as Code Benefits:**

1. **Reproducibility**
   - Same infrastructure configuration for dev, staging, and production
   - Recreate entire environments with a single command
   - No "works on my machine" infrastructure issues

2. **Version Control**
   - Infrastructure changes tracked in Git
   - See who changed what and when
   - Rollback infrastructure changes easily
   - Code review for infrastructure changes

3. **Consistency**
   - Eliminates configuration drift
   - Ensures all environments are identical (except for size/scale)
   - Reduces "works in dev but not in prod" issues

4. **Automation**
   - Infrastructure provisioning integrated into CI/CD pipeline
   - No manual steps required
   - Infrastructure created before application deployment

5. **Documentation**
   - Infrastructure is self-documenting
   - Clear understanding of what resources exist
   - Easy onboarding for new team members

6. **Safety**
   - Preview changes before applying (`terraform plan`)
   - Validate configuration before deployment
   - Prevent accidental resource deletion
   - State management tracks what exists

7. **Multi-Cloud Support**
   - Same tool for AWS, Azure, GCP, Docker, etc.
   - Easy to switch providers or use multiple
   - Consistent workflow across platforms

**Example With Terraform:**
```hcl
# Declarative, version-controlled, reproducible
resource "docker_network" "celery_network" {
  name = "celery-demo-dev-network"
  driver = "bridge"
}

resource "docker_container" "rabbitmq" {
  name  = "celery-demo-dev-rabbitmq"
  image = "rabbitmq:3-management"
  networks_advanced {
    name = docker_network.celery_network.name
  }
}
```

#### 📁 Terraform File Structure

```
terraform/
├── main.tf              # Main configuration, providers, backend
├── rabbitmq.tf          # RabbitMQ service definition
├── variables.tf         # Input variables
├── outputs.tf           # Output values (connection info, etc.)
├── terraform.tfvars.example  # Example variable values
└── .gitignore           # Ignore state files and secrets
```

**Key Files Explained:**

1. **`main.tf`** - Core Configuration
   - Provider configuration (Docker, AWS, Azure, etc.)
   - Backend configuration (where state is stored)
   - Common resources (networks, base infrastructure)

2. **`rabbitmq.tf`** - Service-Specific Resources
   - RabbitMQ container definition
   - Port mappings
   - Health checks
   - Dependencies

3. **`variables.tf`** - Input Variables
   - Environment name (dev/staging/production)
   - Port configurations
   - Resource tags
   - Validation rules

4. **`outputs.tf`** - Output Values
   - Connection strings
   - Resource IDs
   - URLs for services
   - Information needed by other tools

#### 🔄 How Terraform Works

**Terraform Workflow:**

1. **Write Configuration** (`.tf` files)
   ```hcl
   resource "docker_container" "rabbitmq" {
     name  = "rabbitmq"
     image = "rabbitmq:3-management"
   }
   ```

2. **Initialize** (`terraform init`)
   - Downloads providers
   - Sets up backend
   - Prepares working directory

3. **Plan** (`terraform plan`)
   - Shows what will be created/changed/destroyed
   - Validates configuration
   - No changes made yet (safe to review)

4. **Apply** (`terraform apply`)
   - Creates/updates/destroys resources
   - Updates state file
   - Shows what was changed

5. **State Management**
   - Terraform tracks what it created in state file
   - Knows what exists vs. what should exist
   - Can update or destroy resources safely

#### 🚀 Integration with CI/CD

**In Jenkins Pipeline:**

The `Jenkinsfile` includes Terraform stages:

```groovy
stage('Terraform: Validate') {
    // Validates configuration syntax
}

stage('Terraform: Plan') {
    // Shows what infrastructure changes will be made
    // Creates execution plan
}

stage('Terraform: Apply') {
    // Actually provisions/updates infrastructure
    // Runs before application deployment
}
```

**Why This Order:**
1. Infrastructure must exist before deploying applications
2. Validate configuration early (fail fast)
3. Review plan before applying (safety)
4. Apply infrastructure changes
5. Then deploy application to that infrastructure

#### 💡 Real-World Use Cases

**Scenario 1: New Environment Setup**
```bash
# Without Terraform: Hours of manual work, error-prone
# With Terraform: Minutes, automated, reproducible
terraform apply -var="environment=staging"
```

**Scenario 2: Disaster Recovery**
```bash
# Without Terraform: Recreate from memory/documentation (if it exists)
# With Terraform: Recreate from code, guaranteed identical
terraform apply -var="environment=production"
```

**Scenario 3: Infrastructure Updates**
```bash
# Without Terraform: Manual updates, risk of missing something
# With Terraform: Update code, plan, review, apply
terraform plan  # See what will change
terraform apply  # Apply changes safely
```

**Scenario 4: Multi-Environment Consistency**
```bash
# Same code, different variables
terraform apply -var="environment=dev"
terraform apply -var="environment=staging"
terraform apply -var="environment=production"
```

#### 🎓 Key Concepts

**Declarative vs. Imperative:**
- **Imperative (scripts):** "Do this, then that, then this"
- **Declarative (Terraform):** "This is what I want" - Terraform figures out how

**State Management:**
- Terraform tracks what it created
- State file stores resource mappings
- Enables updates and destruction
- Can use remote state for team collaboration

**Idempotency:**
- Running Terraform multiple times is safe
- Won't recreate existing resources
- Only makes necessary changes
- Can run repeatedly without issues

#### 🔧 Common Terraform Commands

```bash
# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Format code
terraform fmt

# Show execution plan
terraform plan -var="environment=dev"

# Apply changes
terraform apply -var="environment=dev"

# Show current state
terraform show

# Destroy infrastructure
terraform destroy -var="environment=dev"

# Get outputs
terraform output
```

#### 🌍 Extending to Cloud Providers

**Current Setup:** Docker (local/on-premise)

**Can Easily Extend To:**

**AWS Example:**
```hcl
provider "aws" {
  region = "us-east-1"
}

resource "aws_ecs_cluster" "main" {
  name = "celery-demo-${var.environment}"
}

resource "aws_rds_instance" "database" {
  engine = "postgres"
  # ...
}
```

**Azure Example:**
```hcl
provider "azurerm" {
  features {}
}

resource "azurerm_container_group" "app" {
  name = "celery-demo-${var.environment}"
  # ...
}
```

**Same Workflow, Different Providers!**

#### ⚠️ Best Practices

1. **Never commit state files** (contains sensitive data)
2. **Use remote state** for team collaboration (S3, Azure Storage, etc.)
3. **Use workspaces** for environment separation
4. **Review plans** before applying
5. **Tag resources** for cost tracking and organization
6. **Use variables** for environment-specific values
7. **Validate before applying** in CI/CD
8. **Backup state files** regularly

#### 📊 Terraform vs. Alternatives

| Feature | Terraform | Manual Setup | Cloud-Specific Tools |
|---------|-----------|--------------|---------------------|
| Version Control | ✅ Yes | ❌ No | ⚠️ Limited |
| Reproducibility | ✅ High | ❌ Low | ⚠️ Medium |
| Multi-Cloud | ✅ Yes | ❌ No | ❌ No |
| Automation | ✅ Full | ❌ Manual | ⚠️ Partial |
| Learning Curve | ⚠️ Medium | ✅ Low | ⚠️ Medium |
| State Management | ✅ Built-in | ❌ None | ⚠️ Limited |

#### 🎯 When to Use Terraform

**Use Terraform When:**
- ✅ You have multiple environments (dev/staging/prod)
- ✅ You need reproducible infrastructure
- ✅ You want infrastructure in version control
- ✅ You're deploying to cloud providers
- ✅ You need to manage infrastructure at scale
- ✅ You want to automate infrastructure provisioning

**You Might Skip Terraform If:**
- ❌ Single environment, never changes
- ❌ Very simple setup (single container)
- ❌ Learning/experimentation only
- ❌ No need for reproducibility

**For This Project:**
- ✅ Multiple environments (dev/staging/production)
- ✅ Need consistency across environments
- ✅ Want automated infrastructure provisioning
- ✅ Professional CI/CD pipeline
- ✅ **Terraform is highly recommended!**

---

## 🔄 How These Files Work Together

### Development Workflow:
```
Developer → docker-compose.yml → Local Testing → Git Push
```

### CI/CD Workflow:
```
Git Push → Jenkinsfile → Build & Test → Registry → Terraform (Provision Infrastructure) → deploy.sh → docker-compose.deploy.yml → Production
```

### Complete Flow Diagram:

```
┌─────────────────┐
│  Developer      │
│  Makes Changes  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Git Repository │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│   Jenkinsfile    │─────▶│  Build & Test    │
│  (Main Pipeline)│      │  Docker Image    │
└────────┬────────┘      └────────┬─────────┘
         │                         │
         │                         ▼
         │                ┌──────────────────┐
         │                │  Docker Registry  │
         │                └────────┬─────────┘
         │                         │
         ▼                         │
┌─────────────────┐                │
│  User Selects   │                │
│  Environment    │                │
└────────┬────────┘                │
         │                         │
         ▼                         │
┌─────────────────┐                │
│  Terraform      │                │
│  (Provision     │                │
│   Infrastructure)│                │
└────────┬────────┘                │
         │                         │
         ▼                         │
┌─────────────────┐                │
│   deploy.sh     │◀───────────────┘
│  (Deployment)   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ docker-compose.deploy.yml│
│  (Production Config)     │
└────────┬─────────────────┘
         │
         ▼
┌─────────────────┐
│  Production     │
│  Environment    │
└─────────────────┘
```

### File Interaction Summary:

1. **`Jenkinsfile`** orchestrates the entire CI/CD process
2. **`terraform/`** provisions infrastructure before deployment
3. **`ci/terraform.sh`** automates Terraform operations
4. **`docker-compose.yml`** is used for local development (not in CI/CD)
5. **`ci/docker-compose.deploy.yml`** is used by `deploy.sh` for deployments
6. **`ci/deploy.sh`** is called by `Jenkinsfile` to perform actual deployment
7. **`Jenkinsfile.staging`** is an alternative simple pipeline (optional)

---

## 🚀 Step-by-Step Setup Guide

### Step 1: Create Project Directory

```bash
mkdir django-celery-project
cd django-celery-project
```

### Step 2: Set Up Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### Step 3: Install Django and Create Project

```bash
# Upgrade pip
pip install --upgrade pip

# Install Django
pip install Django

# Create Django project
django-admin startproject celery_demo .

# Create Django app
python manage.py startapp celery_app
```

### Step 4: Install Required Dependencies

Create `requirements.txt` with the following content:

```txt
Django
djangorestframework
djangorestframework-simplejwt
celery
django-celery-beat
django-celery-results
dj-database-url
gunicorn
amqp
kombu
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Step 5: Configure Django Settings

Edit `celery_demo/settings.py`:

1. **Add apps to INSTALLED_APPS:**
   ```python
   INSTALLED_APPS = [
       'django.contrib.admin',
       'django.contrib.auth',
       'django.contrib.contenttypes',
       'django.contrib.sessions',
       'django.contrib.messages',
       'django.contrib.staticfiles',
       'rest_framework',
       'celery_app',
       'django_celery_results',
       'django_celery_beat',
       'rest_framework_simplejwt',
   ]
   ```

2. **Configure REST Framework:**
   ```python
   REST_FRAMEWORK = {
       'NON_FIELD_ERRORS_KEY': 'errors',
       'DEFAULT_AUTHENTICATION_CLASSES': (
           'rest_framework_simplejwt.authentication.JWTAuthentication',
       )
   }
   ```

3. **Add environment-aware configuration:**
   ```python
   import os
   import dj_database_url
   from pathlib import Path
   
   # Environment helpers
   def env_bool(name: str, default: str = "False") -> bool:
       return os.environ.get(name, default).lower() in ("1", "true", "yes", "on")
   
   def env_list(name: str, default: str = "") -> list[str]:
       raw_value = os.environ.get(name, default)
       return [item.strip() for item in raw_value.split(",") if item.strip()]
   
   # Security settings
   SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "your-secret-key-here")
   DEBUG = env_bool("DJANGO_DEBUG", "True")
   ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
   
   # Database configuration
   DATABASES = {
       "default": dj_database_url.config(
           default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
           conn_max_age=int(os.environ.get("DATABASE_CONN_MAX_AGE", "60")),
           ssl_require=env_bool("DATABASE_SSL_REQUIRE", "False"),
       )
   }
   
   # Celery configuration
   CELERY_BROKER_URL = os.environ.get(
       "CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672/"
   )
   CELERY_RESULT_BACKEND = "django-db"
   CELERY_TIMEZONE = "Asia/Dhaka"
   CELERY_RESULT_EXTENDED = True
   ```

### Step 6: Configure Celery

Create `celery_demo/celery.py`:

```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'celery_demo.settings')

app = Celery('celery_demo')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

Update `celery_demo/__init__.py`:

```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

### Step 7: Create Celery Tasks

Create `celery_demo/tasks.py`:

```python
from celery import shared_task
from django_celery_results.models import TaskResult
from django.utils import timezone
from datetime import timedelta

@shared_task
def clear_session_cache(id):
    print(f"clear session cache: {id}")
    return id

@shared_task
def clear_old_task_result_every_5_minute(text):
    expire_time = timezone.now() - timedelta(minutes=1)
    deleted_count, _ = TaskResult.objects.filter(date_done__lt=expire_time).delete()
    print(f"Deleted {deleted_count} old task results. Message: {text}")
    return {"deleted_count": deleted_count, "message": text}
```

### Step 8: Create Django Models

Edit `celery_app/models.py` with your models (Restaurant, SellerProfile, TemporaryRole, etc.).

### Step 9: Create Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 10: Create Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Step 11: Create Docker Compose File

Create `docker-compose.yml`:

```yaml
version: "3.8"

services:
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
    networks:
      - celery_network

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    ports:
      - "8000:8000"
    depends_on:
      - rabbitmq
    networks:
      - celery_network

  celery:
    build: .
    environment:
      - CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672/
    command: celery -A celery_demo worker --loglevel=info
    depends_on:
      - rabbitmq
    networks:
      - celery_network

networks:
  celery_network:
    driver: bridge
```

### Step 12: Create Environment Configuration Files

Create `deployments/dev.env`:

```env
DJANGO_SECRET_KEY=dev-secret-key-change-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,web
WEB_PORT=8000
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672/
DATABASE_URL=sqlite:////app/db.sqlite3
```

Create similar files for `staging.env` and `production.env` with appropriate values.

### Step 13: Create Deployment Script

Create `ci/deploy.sh`:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

ENVIRONMENT="$1"
IMAGE_TAG="$2"
COMPOSE_FILE="${3:-ci/docker-compose.deploy.yml}"
ENV_FILE="deployments/${ENVIRONMENT}.env"

export APP_IMAGE="${IMAGE_TAG}"
export ENV_FILE="${ENV_FILE}"

docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" pull
docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" run --rm web python manage.py migrate --noinput
docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" up -d --remove-orphans
```

Make it executable:

```bash
chmod +x ci/deploy.sh
```

### Step 14: Create Jenkins Pipeline

Create `Jenkinsfile` (see the existing Jenkinsfile in this repository for the complete implementation).

Key components:
- Slack notification functions
- Multi-stage pipeline (Preparation, Checkout, Test, Build, Deploy)
- Environment-specific deployment stages
- Docker image building and publishing

## 💻 Local Development

### Option 1: Using Docker Compose (Recommended)

1. **Start all services:**
   ```bash
   docker compose up -d
   ```

2. **Run migrations:**
   ```bash
   docker compose exec web python manage.py migrate
   ```

3. **Create superuser:**
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

4. **Access the application:**
   - Web: http://localhost:8000
   - RabbitMQ Management: http://localhost:15672 (guest/guest)

5. **View logs:**
   ```bash
   docker compose logs -f
   ```

6. **Stop services:**
   ```bash
   docker compose down
   ```

### Option 2: Local Python Environment

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Start RabbitMQ (using Docker):**
   ```bash
   docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
   ```

3. **Set environment variables:**
   ```bash
   export DJANGO_SECRET_KEY="your-secret-key"
   export CELERY_BROKER_URL="amqp://guest:guest@localhost:5672/"
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Start Django development server:**
   ```bash
   python manage.py runserver
   ```

6. **Start Celery worker (in another terminal):**
   ```bash
   celery -A celery_demo worker --loglevel=info
   ```

7. **Start Celery beat (optional, for scheduled tasks):**
   ```bash
   celery -A celery_demo beat --loglevel=info
   ```

## 🐳 Docker Setup

### Building the Image

```bash
docker build -t celery-demo:latest .
```

### Running with Docker Compose

```bash
# Development
docker compose up -d

# Production-like
docker compose -f ci/docker-compose.deploy.yml --env-file deployments/production.env up -d
```

### Environment Variables

Docker Compose reads environment variables from:
- `.env` file (if present)
- Environment-specific files in `deployments/`
- Direct environment variable exports

## 🏗️ Terraform Infrastructure Setup

### Initial Setup

1. **Navigate to Terraform directory:**
   ```bash
   cd terraform
   ```

2. **Copy example variables file:**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

3. **Edit variables for your environment:**
   ```bash
   nano terraform.tfvars
   # Update environment, ports, and other settings
   ```

4. **Initialize Terraform:**
   ```bash
   terraform init
   ```
   This downloads required providers and sets up the backend.

### Basic Operations

#### Validate Configuration

```bash
# Check syntax and configuration
terraform validate

# Format code
terraform fmt -recursive
```

#### Plan Changes

```bash
# See what will be created/changed
terraform plan -var="environment=dev"

# Use variables file
terraform plan -var-file="terraform.tfvars"
```

#### Apply Infrastructure

```bash
# Apply changes (creates/updates infrastructure)
terraform apply -var="environment=dev"

# Auto-approve (for CI/CD)
terraform apply -var="environment=dev" -auto-approve
```

#### View Current State

```bash
# Show all resources
terraform show

# Get specific outputs
terraform output

# Get JSON output
terraform output -json
```

#### Destroy Infrastructure

```bash
# Remove all resources
terraform destroy -var="environment=dev"

# Review what will be destroyed first
terraform plan -destroy -var="environment=dev"
```

### Environment-Specific Deployments

#### Development

```bash
cd terraform
terraform workspace new dev 2>/dev/null || terraform workspace select dev
terraform init
terraform plan -var="environment=dev"
terraform apply -var="environment=dev"
```

#### Staging

```bash
cd terraform
terraform workspace new staging 2>/dev/null || terraform workspace select staging
terraform init
terraform plan -var="environment=staging"
terraform apply -var="environment=staging"
```

#### Production

```bash
cd terraform
terraform workspace new production 2>/dev/null || terraform workspace select production
terraform init
terraform plan -var="environment=production"
terraform apply -var="environment=production"  # Review plan carefully!
```

### Using the Terraform Script

The project includes `ci/terraform.sh` for easier automation:

```bash
# Validate
./ci/terraform.sh validate dev

# Plan
./ci/terraform.sh plan dev

# Apply
./ci/terraform.sh apply dev

# Destroy
./ci/terraform.sh destroy dev

# Get outputs
./ci/terraform.sh output dev
```

### Integration with CI/CD

Terraform is automatically executed in the Jenkins pipeline:

1. **Terraform: Validate** - Checks configuration syntax
2. **Terraform: Plan** - Shows what will be created
3. **Terraform: Apply** - Provisions infrastructure
4. **Application Deployment** - Deploys to provisioned infrastructure

To disable Terraform in Jenkins, set:
```groovy
PROVISION_INFRASTRUCTURE = 'false'
```

### State Management

**Local State (Development):**
- State stored in `terraform.tfstate` file
- Good for local development
- Not suitable for team collaboration

**Remote State (Production):**
Configure in `terraform/main.tf`:

```hcl
backend "s3" {
  bucket = "your-terraform-state-bucket"
  key    = "celery-demo/terraform.tfstate"
  region = "us-east-1"
}
```

**Benefits of Remote State:**
- Team collaboration (shared state)
- State locking (prevents conflicts)
- State history and versioning
- Secure storage

### Troubleshooting Terraform

#### Common Issues

**1. State Lock Errors**
```bash
# If Terraform process was interrupted
terraform force-unlock <LOCK_ID>
```

**2. Provider Not Found**
```bash
# Reinitialize providers
terraform init -upgrade
```

**3. Resource Already Exists**
```bash
# Import existing resource
terraform import <resource_type>.<name> <resource_id>
```

**4. Invalid Configuration**
```bash
# Validate and see errors
terraform validate
terraform fmt -check
```

### Best Practices

1. **Always run `terraform plan` before `apply`**
2. **Review plans carefully, especially for production**
3. **Use workspaces for environment separation**
4. **Never commit `.tfstate` files** (contains sensitive data)
5. **Use remote state for production**
6. **Tag resources for cost tracking**
7. **Version control all `.tf` files**
8. **Use variables for environment-specific values**

## 🔄 CI/CD Pipeline Configuration

### Git Branching Strategy

This project uses a simple branching strategy:
- **`main` branch** = Production environment
- **`dev` branch** = Staging environment

**Workflow:**
1. Developer creates feature branch from `dev`
2. Makes changes and commits
3. Creates pull request to `dev` branch
4. GitHub Actions runs CI pipeline (tests, migrations)
5. Code merged to `dev` branch
6. GitHub Actions triggers again (post-merge)
7. Jenkins pipeline deploys to staging (dev branch)
8. After testing, merge `dev` → `main`
9. Jenkins pipeline deploys to production (main branch)

### GitHub Actions CI Pipeline

**File:** `.github/workflows/ci.yml`

**Triggers:**
- Push to `dev` branch
- Pull requests targeting `dev` branch

**Stages:**
1. **Setup Job:**
   - Checkout repository code
   - Install system dependencies
   - Set up Python environment
   - Install Python dependencies
   - Create database migrations
   - Auto-commit migrations (if created)
   - Run migrations in test database
   - Run Django tests
   - Code quality checks (linting)
   - Cleanup workspace

2. **Complete Job:**
   - Final status notification
   - Display build information

**Key Features:**
- Automatic migration generation and commit
- Test execution before deployment
- Code quality validation
- Detailed logging and notifications

**View Pipeline:**
- Go to GitHub repository → Actions tab
- See all workflow runs and their status

### Jenkins Setup

1. **Install Required Plugins:**
   - Pipeline
   - Docker Pipeline
   - Slack Notification
   - Credentials Binding

2. **Configure Credentials:**
   - Docker Registry credentials (ID: `docker-registry-credentials`)
   - Slack webhook or token (ID: set in `SLACK_WEBHOOK_CREDENTIALS_ID` or `SLACK_TOKEN_CREDENTIALS_ID`)

3. **Configure Pipeline:**
   - Create a new Pipeline job
   - Point to your Git repository
   - Set Pipeline script from SCM
   - Branch: `*/main` (or your default branch)
   - Script Path: `Jenkinsfile`

4. **Set Environment Variables:**
   - `SLACK_CHANNEL`: `#your-channel`
   - `IMAGE_REPOSITORY`: `your-registry/celery-demo`
   - `DOCKER_REGISTRY_URL`: `your-registry.com`
   - `DOCKER_CREDENTIALS_ID`: `docker-registry-credentials`

### Jenkins Pipeline Stages

The Jenkins pipeline includes the following stages (in order):

1. **Checkout SCM** - Clean workspace
2. **Checkout Git Repo** - Get source code from repository
3. **Set Up Python** - Create virtual environment
4. **Install Dependencies** - Install Python packages
5. **Static Analysis** - Syntax checking
6. **Run Tests** - Execute Django tests (optional)
7. **Prepare Build Metadata** - Generate image tags
8. **Decrypt Terraform Variables** - Decrypt infrastructure secrets
9. **Build Docker Image** - Build application container
10. **Publish Docker Image** - Push to Docker registry
11. **Terraform: Validate** - Validate infrastructure config
12. **Terraform: Plan** - Preview infrastructure changes
13. **Terraform: Apply** - Provision infrastructure
14. **Collect Static Files** - Gather Django static files
15. **Migrate Database** - Run database migrations
16. **Create Superuser** - Create admin user (if needed)
17. **Deploy** - Deploy to selected environment (dev/staging/production)
18. **Clean Up** - Remove temporary files and containers

### Detailed Pipeline Explanation

For complete line-by-line explanations of all pipeline files, see:
- **[Pipeline Explanation Document](docs/PIPELINE_EXPLANATION.md)** - Detailed explanations of:
  - GitHub Actions workflow (`.github/workflows/ci.yml`)
  - Jenkins pipeline (`Jenkinsfile`)
  - All CI/CD scripts

### Pipeline Stages (Detailed)

1. **Preparation** - Clean workspace
2. **Checkout** - Get source code
3. **Set Up Python** - Create virtual environment
4. **Install Dependencies** - Install Python packages
5. **Static Analysis** - Syntax checking
6. **Run Tests** - Execute Django tests
7. **Prepare Build Metadata** - Generate image tags
8. **Build Docker Image** - Build application image
9. **Publish Docker Image** - Push to registry
10. **Deploy** - Deploy to selected environment (dev/staging/production)

### Running the Pipeline

**Automatic Trigger (Recommended):**
- Pipeline automatically triggers when code is pushed to repository
- Jenkins polls repository or uses webhooks
- Select environment via build parameters

**Manual Trigger:**
1. Go to Jenkins dashboard
2. Select your pipeline job
3. Click "Build with Parameters"
4. Select environment: `dev`, `staging`, or `production`
5. Choose whether to run tests
6. Click "Build"

**Branch Mapping:**
- **dev branch** → Deploy to staging environment
- **main branch** → Deploy to production environment

### Complete CI/CD Flow

```
┌─────────────────┐
│  Developer      │
│  Makes Changes  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Feature Branch │
│  (from dev)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  Pull Request    │─────▶│  GitHub Actions  │
│  to dev branch  │      │  CI Pipeline     │
└────────┬────────┘      └────────┬─────────┘
         │                         │
         │                         ▼
         │                ┌──────────────────┐
         │                │  Run Tests       │
         │                │  Create Migrations│
         │                │  Code Quality    │
         │                └────────┬─────────┘
         │                         │
         ▼                         │
┌─────────────────┐                │
│  Merge to dev   │                │
└────────┬────────┘                │
         │                         │
         ▼                         │
┌─────────────────┐                │
│  GitHub Actions │                │
│  (Post-merge)   │                │
└────────┬────────┘                │
         │                         │
         ▼                         │
┌─────────────────┐                │
│  Jenkins        │◀───────────────┘
│  CD Pipeline    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Deploy to      │
│  Staging        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Testing &      │
│  Validation     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Merge dev →    │
│  main           │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Jenkins        │
│  Deploy to      │
│  Production     │
└─────────────────┘
```

**For detailed line-by-line code explanations, see:**
- **[Pipeline Explanation Document](docs/PIPELINE_EXPLANATION.md)**

## ⚙️ Environment Configuration

### Development (`deployments/dev.env`)

- Debug mode enabled
- SQLite database
- Development server
- Localhost access

### Staging (`deployments/staging.env`)

- Debug disabled
- PostgreSQL database (recommended)
- Gunicorn with multiple workers
- Staging domain configuration

### Production (`deployments/production.env`)

- Debug disabled
- PostgreSQL database (required)
- Gunicorn with optimized workers
- Production domain and security settings
- SSL/TLS configuration

### Important: Update Secrets

**Before deploying, update these values:**

1. `DJANGO_SECRET_KEY` - Generate a secure key:
   ```python
   from django.core.management.utils import get_random_secret_key
   print(get_random_secret_key())
   ```

2. Database credentials
3. Allowed hosts
4. CSRF trusted origins

## 🏃 Running the Application

### Start All Services

```bash
docker compose up -d
```

### Check Service Status

```bash
docker compose ps
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f web
docker compose logs -f celery
```

### Access Services

- **Django Admin**: http://localhost:8000/admin
- **API**: http://localhost:8000/api/
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)

## 🧪 Testing

### Run Django Tests

```bash
# Local
python manage.py test

# Docker
docker compose exec web python manage.py test
```

### Test Celery Tasks

```python
# In Django shell
python manage.py shell

from celery_demo.tasks import clear_session_cache
result = clear_session_cache.delay("test-id")
print(result.get())
```

### Manual Testing

1. **Test API endpoints:**
   ```bash
   curl http://localhost:8000/api/your-endpoint/
   ```

2. **Test Celery worker:**
   - Check logs: `docker compose logs celery`
   - Verify tasks are processed

3. **Test RabbitMQ:**
   - Access management UI
   - Check queues and connections

## 🚢 Deployment

### Manual Deployment

```bash
# Build image
docker build -t your-registry/celery-demo:tag .

# Push to registry
docker push your-registry/celery-demo:tag

# Deploy
./ci/deploy.sh production your-registry/celery-demo:tag
```

### Automated Deployment via Jenkins

1. Push code to repository
2. Trigger Jenkins pipeline
3. Select target environment
4. Monitor Slack notifications
5. Verify deployment

### Post-Deployment Checklist

- [ ] Verify application is accessible
- [ ] Check database migrations applied
- [ ] Verify Celery worker is running
- [ ] Test API endpoints
- [ ] Check logs for errors
- [ ] Verify scheduled tasks are running

## 🔧 Troubleshooting

### Common Issues

#### 1. Celery Worker Not Connecting to RabbitMQ

**Symptoms:** Tasks not executing, connection errors

**Solution:**
```bash
# Check RabbitMQ is running
docker compose ps rabbitmq

# Verify connection string
echo $CELERY_BROKER_URL

# Check RabbitMQ logs
docker compose logs rabbitmq
```

#### 2. Database Migration Errors

**Symptoms:** Migration failures during deployment

**Solution:**
```bash
# Run migrations manually
docker compose exec web python manage.py migrate

# Check migration status
docker compose exec web python manage.py showmigrations
```

#### 3. Docker Build Failures

**Symptoms:** Build errors in Jenkins

**Solution:**
- Check Dockerfile syntax
- Verify all files are in context
- Check requirements.txt for version conflicts
- Review build logs for specific errors

#### 4. Slack Notifications Not Working

**Symptoms:** No Slack messages from pipeline

**Solution:**
- Verify Slack plugin is installed
- Check credentials are configured correctly
- Verify channel name (include `#`)
- Check Jenkins logs for Slack errors

#### 5. Port Conflicts

**Symptoms:** Services can't bind to ports

**Solution:**
```bash
# Check what's using the port
sudo lsof -i :8000

# Change port in docker-compose.yml or .env file
WEB_PORT=8001
```

### Debugging Tips

1. **Check container logs:**
   ```bash
   docker compose logs -f [service-name]
   ```

2. **Access container shell:**
   ```bash
   docker compose exec web bash
   ```

3. **Check environment variables:**
   ```bash
   docker compose exec web env
   ```

4. **Test database connection:**
   ```bash
   docker compose exec web python manage.py dbshell
   ```

5. **Verify Celery configuration:**
   ```bash
   docker compose exec celery celery -A celery_demo inspect active
   ```

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Docker Documentation](https://docs.docker.com/)
- [Jenkins Pipeline Documentation](https://www.jenkins.io/doc/book/pipeline/)
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is provided as-is for educational and demonstration purposes.

## 👥 Support

For issues and questions:
- Check the troubleshooting section
- Review logs and error messages
- Consult the documentation
- Open an issue in the repository

---


