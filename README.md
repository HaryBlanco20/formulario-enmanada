# GymVe

Aplicación **Python** privada para la familia (**Samsung Android** + **iPhone iOS**), sin publicación en tiendas.

| Dispositivo | Cliente |
|-------------|---------|
| **Samsung** | APK **Flet** (`client/`) — sideload |
| **iPhone** | **Safari / PWA** — mismo backend `/login` |

> [`mobile/`](mobile/) (Expo + Supabase) está **obsoleto**; el stack canónico es FastAPI + Postgres + Flet + web PWA.

**Guías**

- [Instalar en celular (Samsung + iPhone)](docs/instalar-en-celular.md)
- [Emulador Android en Ubuntu (+ notas iPhone)](docs/emulador-android-ubuntu.md)
- [Seguridad](docs/seguridad.md)

## Quick start (Ubuntu)

```bash
cp .env.example .env
# Edita secretos, POSTGRES_* y hashes bcrypt de los 4 usuarios

make dev-up          # Postgres healthy → init_db → seed (idempotente)
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- Web / iPhone: `http://127.0.0.1:8000/login` (en iPhone real usa **HTTPS** — túnel o Caddy; ver docs).
- Health: `/health`

HTTPS local opcional: certificados en `docker/caddy/certs/` → `make dev-proxy`.

## Samsung (APK) vs iPhone (PWA)

| | Samsung | iPhone |
|---|---------|--------|
| Instalación | `flet build apk` + sideload | Safari → **Añadir a pantalla de inicio** |
| Dev en Ubuntu | Emulador Android + `adb` | **iPhone físico** + URL HTTPS (no simulador iOS) |
| Auth API | JWT (`/api/v1/login`) | Cookie de sesión web |

```bash
./scripts/build-and-install-apk.sh   # Samsung / emulador
```

## Seguridad (resumen)

- `GYMVE_ENV=production` exige secretos fuertes y `CORS_ORIGINS` explícitos.
- Rate limit en login; política de contraseña en servidor.
- `./scripts/security-check.sh`

Detalle: [docs/seguridad.md](docs/seguridad.md).

## Emulador Android

Requisitos: KVM, SDK Android, licencias aceptadas. Ver [docs/emulador-android-ubuntu.md](docs/emulador-android-ubuntu.md).

```bash
export ANDROID_AVD=Pixel_7_API_34
./scripts/run-android-emulator.sh
```

## API (cliente Flet)

```text
POST /api/v1/login   {"email","password"}  → access_token
GET  /api/v1/me      Authorization: Bearer …
```

## Estructura

```text
app/                 FastAPI + plantillas PWA
client/              Flet (APK Samsung)
docker/              Postgres init, Caddy
scripts/             dev-up, seed, emulador, security-check
docs/
mobile/              Legacy Expo (deprecated)
```

## Calidad

```bash
pip install ruff
make lint
make compose-config
```

## Producción (checklist)

1. `GYMVE_ENV=production`, secretos rotados, `CORS_ORIGINS` con HTTPS del túnel/dominio.
2. Postgres con contraseñas fuertes; backups del volumen `gymve_pgdata`.
3. HTTPS delante del API (Caddy, nginx o túnel).
4. Esquema: [docs/schema-versioning.md](docs/schema-versioning.md).

Licencia: uso privado familiar.
