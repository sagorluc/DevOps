#!/usr/bin/env bash

# Script to collect Django static files
# Used in Jenkins pipeline before deployment

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

echo "Collecting static files for ${ENVIRONMENT} environment..."

# Use docker compose to run collectstatic
if docker compose version >/dev/null 2>&1; then
  docker compose -f "${COMPOSE_FILE}" \
    --env-file "${ENV_FILE}" \
    run --rm web \
    python manage.py collectstatic --noinput --clear
elif command -v docker-compose >/dev/null 2>&1; then
  docker-compose -f "${COMPOSE_FILE}" \
    --env-file "${ENV_FILE}" \
    run --rm web \
    python manage.py collectstatic --noinput --clear
else
  echo "Neither 'docker compose' nor 'docker-compose' is available." >&2
  exit 1
fi

echo "✅ Static files collected successfully"

