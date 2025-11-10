#!/usr/bin/env bash

# Terraform automation script for infrastructure provisioning
# Usage: ./ci/terraform.sh <action> <environment> [terraform-options]
# Actions: init, plan, apply, destroy, validate, fmt

set -Eeuo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <action> <environment> [terraform-options]" >&2
  echo "Actions: init, plan, apply, destroy, validate, fmt" >&2
  exit 1
fi

ACTION="$1"
ENVIRONMENT="$2"
shift 2 || true
TERRAFORM_OPTS=("$@")

TERRAFORM_DIR="${TERRAFORM_DIR:-terraform}"
TF_VAR_FILE="${TF_VAR_FILE:-terraform/${ENVIRONMENT}.tfvars}"
WORKSPACE="${ENVIRONMENT}"

cd "${TERRAFORM_DIR}" || exit 1

# Terraform commands
case "${ACTION}" in
  init)
    echo "Initializing Terraform for ${ENVIRONMENT}..."
    terraform init \
      -backend-config="path=terraform-${ENVIRONMENT}.tfstate" \
      "${TERRAFORM_OPTS[@]}"
    ;;
    
  plan)
    echo "Planning Terraform changes for ${ENVIRONMENT}..."
    terraform workspace select "${WORKSPACE}" 2>/dev/null || terraform workspace new "${WORKSPACE}"
    
    if [[ -f "../${TF_VAR_FILE}" ]]; then
      terraform plan \
        -var-file="../${TF_VAR_FILE}" \
        -var="environment=${ENVIRONMENT}" \
        -out="tfplan-${ENVIRONMENT}" \
        "${TERRAFORM_OPTS[@]}"
    else
      terraform plan \
        -var="environment=${ENVIRONMENT}" \
        -out="tfplan-${ENVIRONMENT}" \
        "${TERRAFORM_OPTS[@]}"
    fi
    ;;
    
  apply)
    echo "Applying Terraform changes for ${ENVIRONMENT}..."
    terraform workspace select "${WORKSPACE}" 2>/dev/null || terraform workspace new "${WORKSPACE}"
    
    if [[ -f "tfplan-${ENVIRONMENT}" ]]; then
      terraform apply "tfplan-${ENVIRONMENT}"
    else
      if [[ -f "../${TF_VAR_FILE}" ]]; then
        terraform apply \
          -var-file="../${TF_VAR_FILE}" \
          -var="environment=${ENVIRONMENT}" \
          -auto-approve \
          "${TERRAFORM_OPTS[@]}"
      else
        terraform apply \
          -var="environment=${ENVIRONMENT}" \
          -auto-approve \
          "${TERRAFORM_OPTS[@]}"
      fi
    fi
    ;;
    
  destroy)
    echo "Destroying Terraform infrastructure for ${ENVIRONMENT}..."
    terraform workspace select "${WORKSPACE}" 2>/dev/null || {
      echo "Workspace ${WORKSPACE} does not exist. Nothing to destroy." >&2
      exit 0
    }
    
    if [[ -f "../${TF_VAR_FILE}" ]]; then
      terraform destroy \
        -var-file="../${TF_VAR_FILE}" \
        -var="environment=${ENVIRONMENT}" \
        "${TERRAFORM_OPTS[@]}"
    else
      terraform destroy \
        -var="environment=${ENVIRONMENT}" \
        "${TERRAFORM_OPTS[@]}"
    fi
    ;;
    
  validate)
    echo "Validating Terraform configuration..."
    terraform validate
    ;;
    
  fmt)
    echo "Formatting Terraform files..."
    terraform fmt -recursive
    ;;
    
  output)
    echo "Getting Terraform outputs for ${ENVIRONMENT}..."
    terraform workspace select "${WORKSPACE}" 2>/dev/null || {
      echo "Workspace ${WORKSPACE} does not exist." >&2
      exit 1
    }
    terraform output -json
    ;;
    
  *)
    echo "Unknown action: ${ACTION}" >&2
    echo "Valid actions: init, plan, apply, destroy, validate, fmt, output" >&2
    exit 1
    ;;
esac

