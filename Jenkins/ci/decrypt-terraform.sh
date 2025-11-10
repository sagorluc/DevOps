#!/usr/bin/env bash

# Script to decrypt Terraform variables
# Supports various encryption methods (SOPS, GPG, etc.)

set -Eeuo pipefail

ENVIRONMENT="${1:-dev}"
TERRAFORM_DIR="${TERRAFORM_DIR:-terraform}"
ENCRYPTED_FILE="${TERRAFORM_DIR}/${ENVIRONMENT}.tfvars.encrypted"
DECRYPTED_FILE="${TERRAFORM_DIR}/${ENVIRONMENT}.tfvars"

if [[ ! -f "${ENCRYPTED_FILE}" ]]; then
  echo "No encrypted file found at ${ENCRYPTED_FILE}, skipping decryption"
  exit 0
fi

# Method 1: Using SOPS (Secrets Operations)
if command -v sops >/dev/null 2>&1; then
  echo "Decrypting Terraform variables using SOPS..."
  sops -d "${ENCRYPTED_FILE}" > "${DECRYPTED_FILE}"
  chmod 600 "${DECRYPTED_FILE}"
  echo "✅ Variables decrypted to ${DECRYPTED_FILE}"
  exit 0
fi

# Method 2: Using GPG
if command -v gpg >/dev/null 2>&1 && [[ -n "${GPG_KEY_ID:-}" ]]; then
  echo "Decrypting Terraform variables using GPG..."
  gpg --decrypt --output "${DECRYPTED_FILE}" "${ENCRYPTED_FILE}" 2>/dev/null || {
    echo "GPG decryption failed. Ensure GPG_KEY_ID is set and key is available."
    exit 1
  }
  chmod 600 "${DECRYPTED_FILE}"
  echo "✅ Variables decrypted to ${DECRYPTED_FILE}"
  exit 0
fi

# Method 3: Using base64 (simple, not secure - for development only)
if [[ "${ENVIRONMENT}" == "dev" ]] && [[ -f "${ENCRYPTED_FILE}" ]]; then
  echo "Warning: Using base64 decryption (development only)"
  base64 -d "${ENCRYPTED_FILE}" > "${DECRYPTED_FILE}" 2>/dev/null || {
    echo "Base64 decryption failed"
    exit 1
  }
  chmod 600 "${DECRYPTED_FILE}"
  echo "✅ Variables decrypted to ${DECRYPTED_FILE}"
  exit 0
fi

echo "No decryption method available. Please install SOPS or configure GPG."
exit 1

