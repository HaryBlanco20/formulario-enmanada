#!/usr/bin/env bash
# Falla si detecta secretos por defecto o configuración peligrosa en producción.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail=0

warn() { echo "WARN: $*"; }
err() { echo "ERROR: $*"; fail=1; }

if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  source "$ROOT/scripts/load_env.sh"
  load_env_file "$ROOT/.env"
else
  warn "No hay .env (solo comprobando repo)."
fi

weak_session='cambia-esto-por-un-secreto-largo-y-aleatorio-de-al-menos-32'
if [[ -f .env ]] && [[ "${SESSION_SECRET:-}" == "$weak_session" ]]; then
  err "SESSION_SECRET sigue siendo el valor de ejemplo."
fi

if [[ -f .env ]] && [[ ${#SESSION_SECRET} -lt 32 ]]; then
  err "SESSION_SECRET debe tener al menos 32 caracteres."
fi

if [[ "${GYMVE_ENV:-development}" =~ ^(production|prod)$ ]]; then
  if [[ "${CORS_ORIGINS:-}" == "*" || -z "${CORS_ORIGINS:-}" ]]; then
    err "En producción, CORS_ORIGINS no puede ser '*' ni estar vacío."
  fi
  if [[ "${POSTGRES_PASSWORD:-}" == "gymve" ]]; then
    err "POSTGRES_PASSWORD por defecto 'gymve' no permitido en producción."
  fi
  if [[ "${GYMVE_ALLOW_INSECURE_DEV:-}" =~ ^(1|true|yes)$ ]]; then
    err "GYMVE_ALLOW_INSECURE_DEV activo en producción."
  fi
fi

if grep -R --line-number -E '(PASSWORD=.*[^=]|SESSION_SECRET=.*[^=])' .env.example >/dev/null 2>&1; then
  : # .env.example solo placeholders
fi

if git grep -n 'cambia-esto-por-un-secreto' -- ':!.env.example' ':!docs/**' ':!scripts/security-check.sh' ':!app/config.py' 2>/dev/null; then
  err "Texto de secreto de ejemplo encontrado fuera de .env.example/docs."
fi

if [[ "$fail" -ne 0 ]]; then
  echo "security-check: FALLO"
  exit 1
fi
echo "security-check: OK"
