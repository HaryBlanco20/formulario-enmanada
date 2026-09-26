#!/usr/bin/env bash
# Arranque idempotente: Postgres healthy → init_db → seed_users
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  echo "Falta .env — copia desde .env.example y define secretos."
  exit 1
fi

if ! grep -q '^POSTGRES_PASSWORD=' .env; then
  echo ".env incompleto (POSTGRES_PASSWORD)."
  exit 1
fi
# shellcheck disable=SC1091
source "$ROOT/scripts/load_env.sh"
load_env_file "$ROOT/.env"

docker compose up -d postgres

echo "Esperando Postgres..."
for _ in $(seq 1 60); do
  if docker compose exec -T postgres pg_isready -U "${POSTGRES_SUPERUSER:-postgres}" -d "${POSTGRES_DB:-gymve}" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! docker compose exec -T postgres pg_isready -U "${POSTGRES_SUPERUSER:-postgres}" -d "${POSTGRES_DB:-gymve}" >/dev/null 2>&1; then
  echo "Postgres no respondió a tiempo."
  exit 1
fi

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt

python scripts/init_db.py
python scripts/seed_users.py

echo ""
echo "Listo. Inicia el API:"
echo "  source .venv/bin/activate && uvicorn app.main:app --host \${GYMVE_HOST:-0.0.0.0} --port \${GYMVE_PORT:-8000}"
echo ""
echo "Clientes: Samsung (APK Flet) + iPhone (Safari PWA) — docs/instalar-en-celular.md"
