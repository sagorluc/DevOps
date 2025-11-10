# Complete Pipeline Explanation - Line by Line

This document provides detailed line-by-line explanations of all CI/CD pipeline files.

## Table of Contents

1. [GitHub Actions Workflow (.github/workflows/ci.yml)](#github-actions-workflow)
2. [Jenkins Pipeline (Jenkinsfile)](#jenkins-pipeline)
3. [CI Scripts](#ci-scripts)

---

## GitHub Actions Workflow

**File:** `.github/workflows/ci.yml`

### Overview
This workflow runs automatically when code is merged to the `dev` branch. It performs CI tasks like testing, creating migrations, and preparing code for deployment.

### Line-by-Line Explanation

```yaml
# GitHub Actions CI Pipeline
# Triggers when code is merged to dev branch
# This pipeline runs tests, creates migrations, and prepares the code for deployment

name: CI Pipeline
```
- **Line 1-3:** Comments explaining the file's purpose
- **Line 5:** `name:` - Defines the workflow name shown in GitHub Actions UI

```yaml
on:
  push:
    branches:
      - dev
  pull_request:
    branches:
      - dev
```
- **Line 6-11:** `on:` - Defines when the workflow triggers
  - **Line 7-9:** Triggers on push to `dev` branch
  - **Line 10-11:** Also triggers on pull requests targeting `dev` branch

```yaml
env:
  PYTHON_VERSION: '3.9'
  DJANGO_SETTINGS_MODULE: 'celery_demo.settings'
```
- **Line 13-15:** `env:` - Global environment variables for all jobs
  - **Line 14:** Python version to use
  - **Line 15:** Django settings module path

```yaml
jobs:
  setup-job:
    name: Setup Job
    runs-on: ubuntu-latest
```
- **Line 17-20:** Defines jobs (work units)
  - **Line 18:** Job ID `setup-job`
  - **Line 19:** Display name
  - **Line 20:** Runs on latest Ubuntu runner

```yaml
    steps:
      - name: Run action/checkout@v4
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.GITHUB_TOKEN }}
```
- **Line 22-27:** Steps in the job
  - **Line 23:** Step name
  - **Line 24:** Uses official checkout action (v4)
  - **Line 25-27:** Configuration
    - **Line 26:** `fetch-depth: 0` - Fetch full git history (needed for migration detection)
    - **Line 27:** Use GitHub token for authentication

```yaml
      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            python3-dev \
            python3-pip \
            python3-venv \
            postgresql-client \
            libpq-dev \
            build-essential \
            git
```
- **Line 29-38:** Install system packages
  - **Line 30:** Update package list
  - **Line 31-37:** Install required packages:
    - `python3-dev`: Python development headers
    - `python3-pip`: Python package manager
    - `python3-venv`: Virtual environment support
    - `postgresql-client`: PostgreSQL client tools
    - `libpq-dev`: PostgreSQL development libraries
    - `build-essential`: Build tools (gcc, make, etc.)
    - `git`: Git version control

```yaml
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
```
- **Line 40-44:** Set up Python environment
  - **Line 41:** Uses official Python setup action
  - **Line 43:** Uses Python version from env variable
  - **Line 44:** Cache pip packages for faster builds

```yaml
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip wheel setuptools
          pip install -r requirements.txt
          pip install flake8 black
```
- **Line 46-50:** Install Python dependencies
  - **Line 47:** Upgrade pip, wheel, setuptools
  - **Line 48:** Install project dependencies
  - **Line 49:** Install code quality tools (optional)

```yaml
      - name: Create migrations
        run: |
          python manage.py makemigrations --noinput
          python manage.py makemigrations celery_app --noinput || true
        continue-on-error: true
```
- **Line 52-56:** Create database migrations
  - **Line 53:** Create migrations for all apps (no user input)
  - **Line 54:** Create migrations for celery_app (continue if fails)
  - **Line 55:** Don't fail job if migrations already exist

```yaml
      - name: Check migration status
        id: check-migrations
        run: |
          if [ -n "$(git status --porcelain celery_app/migrations/ celery_demo/migrations/ 2>/dev/null)" ]; then
            echo "migrations_exist=true" >> $GITHUB_OUTPUT
            echo "New migrations detected"
          else
            echo "migrations_exist=false" >> $GITHUB_OUTPUT
            echo "No new migrations"
          fi
```
- **Line 58-67:** Check if new migrations were created
  - **Line 59:** Set step ID for later reference
  - **Line 60-66:** Check git status for migration files
    - If files changed: set `migrations_exist=true`
    - Otherwise: set `migrations_exist=false`
  - Output is available in `steps.check-migrations.outputs.migrations_exist`

```yaml
      - name: Commit migrations
        if: steps.check-migrations.outputs.migrations_exist == 'true'
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add celery_app/migrations/ celery_demo/migrations/ || true
          git commit -m "ci: Auto-generate database migrations [skip ci]" || exit 0
          git push origin HEAD:dev || exit 0
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
- **Line 69-78:** Auto-commit migrations if created
  - **Line 70:** Only run if migrations exist
  - **Line 71-72:** Configure git user (required for commits)
  - **Line 73:** Stage migration files
  - **Line 74:** Commit with message (skip CI to avoid loop)
  - **Line 75:** Push to dev branch
  - **Line 76-77:** Set GitHub token for authentication

```yaml
      - name: Post setup migrations
        run: |
          python manage.py migrate --noinput
          python manage.py check --deploy
```
- **Line 80-83:** Run migrations and check deployment readiness
  - **Line 81:** Apply migrations to test database
  - **Line 82:** Run Django deployment checklist

```yaml
      - name: Run tests
        run: |
          python manage.py test --verbosity=2
        continue-on-error: true
```
- **Line 85-88:** Run Django test suite
  - **Line 86:** Run tests with verbose output
  - **Line 87:** Continue even if tests fail (for now)

```yaml
      - name: Lint code
        run: |
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
          flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics || true
        continue-on-error: true
```
- **Line 90-94:** Code quality checks
  - **Line 91:** Check for critical errors (syntax, undefined names)
  - **Line 92:** Check for style issues (non-blocking)

```yaml
      - name: Post run action/checkout@v4
        if: always()
        run: |
          echo "Cleaning up workspace..."
          rm -rf .venv __pycache__ */__pycache__ */*/__pycache__
          find . -type d -name "__pycache__" -exec rm -r {} + || true
          find . -type f -name "*.pyc" -delete || true
```
- **Line 96-101:** Cleanup step
  - **Line 97:** Always run (even on failure)
  - **Line 98-100:** Remove Python cache files and virtual environment

```yaml
  complete-job:
    name: Complete Job
    runs-on: ubuntu-latest
    needs: setup-job
    if: always()
```
- **Line 103-107:** Second job for completion notification
  - **Line 104:** Job name
  - **Line 105:** Run on Ubuntu
  - **Line 106:** Wait for setup-job to finish
  - **Line 107:** Run regardless of setup-job result

```yaml
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Job completion status
        run: |
          echo "CI Pipeline completed"
          echo "Branch: ${{ github.ref }}"
          echo "Commit: ${{ github.sha }}"
          echo "Author: ${{ github.actor }}"
```
- **Line 109-116:** Completion steps
  - **Line 110-111:** Checkout code
  - **Line 113-116:** Print completion status with context

---

## Jenkins Pipeline

**File:** `Jenkinsfile`

### Overview
This Jenkins pipeline handles the complete CD (Continuous Deployment) process, from code checkout to production deployment.

### Line-by-Line Explanation

#### Function Definitions (Lines 1-36)

```groovy
def slackColorFor(status) {
    switch (status?.toUpperCase()) {
        case 'SUCCESS':
            return '#2EB67D'
        case 'FAILURE':
        case 'FAILED':
            return '#E01E5A'
        case 'ABORTED':
            return '#9E9E9E'
        case 'UNSTABLE':
            return '#ECB22E'
        default:
            return '#439FE0'
    }
}
```
- **Line 1:** Define function to get Slack color by status
- **Line 2:** Convert status to uppercase (safe if null)
- **Line 3-4:** Success = green
- **Line 5-6:** Failure = red
- **Line 7-8:** Aborted = gray
- **Line 9-10:** Unstable = yellow
- **Line 11-12:** Default = blue

```groovy
def notifySlack(String stageName, String status, String customMessage = null, String explicitColor = null) {
    if (!env.SLACK_CHANNEL?.trim()) {
        echo "Slack channel not configured; skipping notification for ${stageName} (${status})."
        return
    }
```
- **Line 17:** Function to send Slack notifications
  - Parameters: stage name, status, optional custom message, optional color
- **Line 18-21:** Check if Slack channel configured, skip if not

```groovy
    def color = explicitColor ?: slackColorFor(status)
    def normalizedStatus = status?.toUpperCase() ?: 'UNKNOWN'
    def message = customMessage ?: "*${env.JOB_NAME}* <${env.BUILD_URL}|#${env.BUILD_NUMBER}> `${normalizedStatus}` at stage *${stageName}* (environment: `${params?.DEPLOY_ENV}`)"
```
- **Line 23:** Use explicit color or determine from status
- **Line 24:** Normalize status to uppercase
- **Line 25:** Build message with job name, build link, status, stage, environment

```groovy
    if (env.SLACK_WEBHOOK_CREDENTIALS_ID?.trim()) {
        withCredentials([string(credentialsId: env.SLACK_WEBHOOK_CREDENTIALS_ID, variable: 'SLACK_WEBHOOK')]) {
            slackSend(channel: env.SLACK_CHANNEL, color: color, message: message, webhookUrl: SLACK_WEBHOOK)
        }
    } else if (env.SLACK_TOKEN_CREDENTIALS_ID?.trim()) {
        slackSend(channel: env.SLACK_CHANNEL, color: color, message: message, tokenCredentialId: env.SLACK_TOKEN_CREDENTIALS_ID)
    } else {
        slackSend(channel: env.SLACK_CHANNEL, color: color, message: message)
    }
}
```
- **Line 27-29:** If webhook credential ID set, use webhook method
- **Line 30-32:** Else if token credential ID set, use token method
- **Line 33-34:** Else use default Slack plugin configuration

#### Pipeline Definition (Lines 38-77)

```groovy
pipeline {
    agent any
```
- **Line 38:** Declare Jenkins pipeline
- **Line 39:** Run on any available agent

```groovy
    options {
        ansiColor('xterm')
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '30'))
        disableConcurrentBuilds()
        skipDefaultCheckout()
    }
```
- **Line 41-47:** Pipeline options
  - **Line 42:** Enable ANSI color output
  - **Line 43:** Add timestamps to console output
  - **Line 44:** Keep last 30 builds
  - **Line 45:** Don't run multiple builds simultaneously
  - **Line 46:** Skip automatic checkout (we'll do it manually)

```groovy
    parameters {
        choice(
            name: 'DEPLOY_ENV',
            choices: ['dev', 'staging', 'production'],
            description: 'Select the target environment for deployment.'
        )
        booleanParam(
            name: 'RUN_TESTS',
            defaultValue: true,
            description: 'Run Django unit tests before building the Docker image.'
        )
    }
```
- **Line 49-60:** Build parameters
  - **Line 50-54:** Environment choice (dev/staging/production)
  - **Line 55-59:** Boolean to run tests (default: true)

```groovy
    environment {
        PROJECT_NAME = 'celery-demo'
        PYTHON_BIN = 'python3'
        VENV_PATH = '.venv'
        IMAGE_REPOSITORY = 'registry.example.com/celery-demo'
        DOCKER_REGISTRY_URL = 'registry.example.com'
        DOCKER_CREDENTIALS_ID = 'docker-registry-credentials'
        DEV_DOCKER_CONTEXT = ''
        STAGING_DOCKER_CONTEXT = ''
        PRODUCTION_DOCKER_CONTEXT = ''
        SLACK_CHANNEL = '#celery-cicd'
        SLACK_WEBHOOK_CREDENTIALS_ID = ''
        SLACK_TOKEN_CREDENTIALS_ID = ''
        TERRAFORM_DIR = 'terraform'
        PROVISION_INFRASTRUCTURE = 'true'
    }
```
- **Line 62-77:** Environment variables
  - **Line 63:** Project name
  - **Line 64-65:** Python configuration
  - **Line 66-68:** Docker registry settings
  - **Line 69-71:** Docker contexts for remote deployments
  - **Line 72-74:** Slack configuration
  - **Line 75-76:** Terraform configuration

#### Pipeline Stages

**Stage: Checkout SCM (Lines 80-99)**
```groovy
stage('Checkout SCM') {
    steps {
        script { notifySlack('Checkout SCM', 'STARTED') }
        cleanWs()
    }
```
- **Line 80:** Stage name
- **Line 82:** Send Slack notification
- **Line 83:** Clean workspace

**Stage: Checkout Git Repo (Lines 101-125)**
```groovy
stage('Checkout Git Repo') {
    steps {
        script { notifySlack('Checkout Git Repo', 'STARTED') }
        checkout scm
        sh '''
            git branch -a
            git log -1 --oneline
            echo "Current branch: $(git rev-parse --abbrev-ref HEAD)"
        '''
    }
```
- **Line 101:** Stage name
- **Line 103:** Notify Slack
- **Line 104:** Checkout source code from SCM
- **Line 105-108:** Display git information

**Stage: Decrypt Terraform Variables (Lines 261-290)**
```groovy
stage('Decrypt Terraform Variables') {
    when {
        expression { env.PROVISION_INFRASTRUCTURE == 'true' }
    }
    steps {
        script { notifySlack('Decrypt Terraform Variables', 'STARTED') }
        sh '''
            set -e
            if [ -f "ci/decrypt-terraform.sh" ]; then
                ./ci/decrypt-terraform.sh ${DEPLOY_ENV}
            else
                echo "Decrypt script not found, skipping..."
            fi
        '''
    }
```
- **Line 261:** Stage name
- **Line 262-264:** Only run if infrastructure provisioning enabled
- **Line 266:** Notify Slack
- **Line 267-273:** Run decryption script if exists

**Stage: Build Docker Image (Lines 292-310)**
```groovy
stage('Build Docker Image') {
    steps {
        script { notifySlack('Build Docker Image', 'STARTED') }
        sh '''
            set -e
            docker build \
              --pull \
              --build-arg BUILD_ENV=${DEPLOY_ENV} \
              -t ${IMAGE_FULL_NAME} .
        '''
    }
```
- **Line 292:** Stage name
- **Line 294:** Notify Slack
- **Line 295-300:** Build Docker image
  - `--pull`: Always pull base image
  - `--build-arg`: Pass environment to build
  - `-t`: Tag image with full name

**Stage: Collect Static Files (Lines 453-482)**
```groovy
stage('Collect Static Files') {
    steps {
        script { notifySlack('Collect Static Files', 'STARTED') }
        sh '''
            set -e
            if [ -f "ci/collect-static.sh" ]; then
                ./ci/collect-static.sh ${DEPLOY_ENV} ci/docker-compose.deploy.yml ${IMAGE_FULL_NAME}
            else
                echo "Collect static script not found, using docker compose directly..."
                export APP_IMAGE="${IMAGE_FULL_NAME}"
                export ENV_FILE="deployments/${DEPLOY_ENV}.env"
                docker compose -f ci/docker-compose.deploy.yml --env-file deployments/${DEPLOY_ENV}.env run --rm web python manage.py collectstatic --noinput --clear
            fi
        '''
    }
```
- **Line 453:** Stage name
- **Line 455:** Notify Slack
- **Line 456-465:** Collect Django static files
  - Try script first, fallback to direct docker compose

**Stage: Migrate Database (Lines 484-513)**
```groovy
stage('Migrate Database') {
    steps {
        script { notifySlack('Migrate Database', 'STARTED') }
        sh '''
            set -e
            if [ -f "ci/migrate-db.sh" ]; then
                ./ci/migrate-db.sh ${DEPLOY_ENV} ci/docker-compose.deploy.yml ${IMAGE_FULL_NAME}
            else
                echo "Migrate script not found, using docker compose directly..."
                export APP_IMAGE="${IMAGE_FULL_NAME}"
                export ENV_FILE="deployments/${DEPLOY_ENV}.env"
                docker compose -f ci/docker-compose.deploy.yml --env-file deployments/${DEPLOY_ENV}.env run --rm web python manage.py migrate --noinput
            fi
        '''
    }
```
- **Line 484:** Stage name
- **Line 486:** Notify Slack
- **Line 487-496:** Run database migrations
  - Uses script or direct docker compose

**Stage: Create Superuser (Lines 515-541)**
```groovy
stage('Create Superuser') {
    steps {
        script { notifySlack('Create Superuser', 'STARTED') }
        sh '''
            set -e
            if [ -f "ci/create-superuser.sh" ]; then
                ./ci/create-superuser.sh ${DEPLOY_ENV} ci/docker-compose.deploy.yml ${IMAGE_FULL_NAME}
            else
                echo "Create superuser script not found, skipping..."
            fi
        '''
    }
```
- **Line 515:** Stage name
- **Line 517:** Notify Slack
- **Line 518-524:** Create Django superuser if script exists

**Stage: Clean Up (Lines 627-665)**
```groovy
stage('Clean Up') {
    steps {
        script { notifySlack('Clean Up', 'STARTED') }
        sh '''
            set -e
            echo "Cleaning up temporary files and containers..."
            
            # Remove temporary Terraform files if decrypted
            rm -f terraform/*.tfvars 2>/dev/null || true
            
            # Clean up Docker build cache (optional)
            docker system prune -f --volumes || true
            
            # Remove dangling images
            docker image prune -f || true
            
            # Clean up workspace
            find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
            find . -type f -name "*.pyc" -delete 2>/dev/null || true
            rm -rf .venv *.egg-info 2>/dev/null || true
            
            echo "✅ Cleanup completed"
        '''
    }
```
- **Line 627:** Stage name
- **Line 629:** Notify Slack
- **Line 630-646:** Cleanup operations
  - Remove decrypted Terraform files
  - Prune Docker system
  - Remove Python cache files
  - Remove virtual environment

---

## CI Scripts

### decrypt-terraform.sh

**Purpose:** Decrypt Terraform variable files before use

**Key Lines:**
- **Line 3:** `set -Eeuo pipefail` - Exit on error, undefined vars, pipe failures
- **Line 5-8:** Get environment and file paths
- **Line 17-20:** Check if encrypted file exists
- **Line 23-26:** Try SOPS decryption (if available)
- **Line 30-36:** Try GPG decryption (if available)
- **Line 40-47:** Fallback to base64 (dev only)

### collect-static.sh

**Purpose:** Collect Django static files for production

**Key Lines:**
- **Line 5-9:** Validate arguments
- **Line 11-13:** Set environment variables
- **Line 15-25:** Use docker compose to run collectstatic
  - `--noinput`: Don't prompt for input
  - `--clear`: Clear existing static files first

### migrate-db.sh

**Purpose:** Run database migrations

**Key Lines:**
- **Line 5-9:** Validate arguments
- **Line 11-13:** Set environment variables
- **Line 15-25:** Use docker compose to run migrations
  - `--noinput`: Don't prompt for confirmation

### create-superuser.sh

**Purpose:** Create Django superuser if it doesn't exist

**Key Lines:**
- **Line 5-9:** Validate arguments
- **Line 11-13:** Set environment variables
- **Line 15-19:** Get superuser credentials from environment
- **Line 21-25:** Skip if password not set
- **Line 27-45:** Use docker compose to create superuser via Django shell

---

## Complete Pipeline Flow

1. **GitHub Actions (CI):**
   - Triggered on merge to `dev` branch
   - Checkout code
   - Install dependencies
   - Create migrations
   - Auto-commit migrations
   - Run tests
   - Code quality checks

2. **Jenkins (CD):**
   - Checkout code from repository
   - Decrypt Terraform variables
   - Provision infrastructure (Terraform)
   - Build Docker image
   - Publish to registry
   - Collect static files
   - Run migrations
   - Create superuser
   - Deploy application
   - Clean up

This creates a complete CI/CD pipeline from code commit to production deployment!

