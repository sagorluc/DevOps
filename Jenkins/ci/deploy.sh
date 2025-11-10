#!/usr/bin/env bash

set -Eeuo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <environment> <image-tag> [compose-file]" >&2
  exit 64
fi

ENVIRONMENT="$1"
IMAGE_TAG="$2"
COMPOSE_FILE="${3:-ci/docker-compose.deploy.yml}"
PROJECT_NAME="${PROJECT_NAME:-celery-demo}"
ENV_DIR="${ENV_DIR:-deployments}"
ENV_FILE="${ENV_DIR}/${ENVIRONMENT}.env"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Environment file '${ENV_FILE}' not found." >&2
  exit 65
fi

UPPER_ENVIRONMENT="${ENVIRONMENT^^}"
CONTEXT_VAR_NAME="${UPPER_ENVIRONMENT}_DOCKER_CONTEXT"
DOCKER_CONTEXT="${!CONTEXT_VAR_NAME:-}"

compose() {
  local docker_cmd=("docker")
  if [[ -n "${DOCKER_CONTEXT}" ]]; then
    docker_cmd+=("--context" "${DOCKER_CONTEXT}")
  fi

  if docker compose version >/dev/null 2>&1; then
    "${docker_cmd[@]}" compose "$@"
  elif command -v docker-compose >/dev/null 2>&1; then
    docker-compose "$@"
  else
    echo "Neither 'docker compose' nor 'docker-compose' is available on PATH." >&2
    exit 66
  fi
}

export APP_IMAGE="${IMAGE_TAG}"
export ENV_FILE="${ENV_FILE}"
export DEPLOY_ENVIRONMENT="${ENVIRONMENT}"

COMPOSE_ARGS=(
  -f "${COMPOSE_FILE}"
  --project-name "${PROJECT_NAME}-${ENVIRONMENT}"
  --env-file "${ENV_FILE}"
)

echo "Deploying ${APP_IMAGE} to ${ENVIRONMENT} using ${COMPOSE_FILE}"

compose "${COMPOSE_ARGS[@]}" pull
compose "${COMPOSE_ARGS[@]}" run --rm web python manage.py migrate --noinput
compose "${COMPOSE_ARGS[@]}" up -d --remove-orphans
compose "${COMPOSE_ARGS[@]}" ps

