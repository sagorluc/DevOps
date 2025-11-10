#!/usr/bin/env bash

# Script to create Django superuser if it doesn't exist
# Used in Jenkins pipeline during deployment

set -Eeuo pipefail

ENVIRONMENT="${1:-dev}"
COMPOSE_FILE="${2:-ci/docker-compose.deploy.yml}"
ENV_FILE="deployments/${ENVIRONMENT}.env"
IMAGE_TAG="${3:-}"

if [[ -z "${IMAGE_TAG}" ]]; then
  echo "Usage: $0 <environment> <compose-file> <image-tag>" >&2
  exit 1
fi

export APP_IMAGE="${IMAGE_TAG}"
export ENV_FILE="${ENV_FILE}"

# Get superuser credentials from environment or use defaults
SUPERUSER_USERNAME="${DJANGO_SUPERUSER_USERNAME:-admin}"
SUPERUSER_EMAIL="${DJANGO_SUPERUSER_EMAIL:-admin@example.com}"
SUPERUSER_PASSWORD="${DJANGO_SUPERUSER_PASSWORD:-}"

if [[ -z "${SUPERUSER_PASSWORD}" ]]; then
  echo "Warning: DJANGO_SUPERUSER_PASSWORD not set. Skipping superuser creation."
  echo "Superuser will need to be created manually."
  exit 0
fi

echo "Creating superuser for ${ENVIRONMENT} environment..."

# Use docker compose to create superuser
if docker compose version >/dev/null 2>&1; then
  docker compose -f "${COMPOSE_FILE}" \
    --env-file "${ENV_FILE}" \
    run --rm web \
    python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='${SUPERUSER_USERNAME}').exists():
    User.objects.create_superuser('${SUPERUSER_USERNAME}', '${SUPERUSER_EMAIL}', '${SUPERUSER_PASSWORD}')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
EOF
elif command -v docker-compose >/dev/null 2>&1; then
  docker-compose -f "${COMPOSE_FILE}" \
    --env-file "${ENV_FILE}" \
    run --rm web \
    python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='${SUPERUSER_USERNAME}').exists():
    User.objects.create_superuser('${SUPERUSER_USERNAME}', '${SUPERUSER_EMAIL}', '${SUPERUSER_PASSWORD}')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
EOF
else
  echo "Neither 'docker compose' nor 'docker-compose' is available." >&2
  exit 1
fi

echo "✅ Superuser creation completed"

