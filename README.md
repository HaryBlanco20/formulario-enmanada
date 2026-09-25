# GymVe

Aplicación **Python** privada para la familia (iPhone y Android), **sin publicación** en App Store ni Play Store.

**Stack canónico:** **FastAPI + PostgreSQL** (servidor) y **Flet** (APK Android). **iPhone:** web/PWA en Safari. Login en español, 4 usuarios, contraseña ≥10 caracteres + carácter especial.

> La carpeta [`mobile/`](mobile/) (Expo/React Native + Supabase) quedó **obsoleta** respecto a este README; no la uses para nuevas funciones. El backend Python y Postgres sustituyen Supabase para auth.

Guía de instalación en celulares: **[docs/instalar-en-celular.md](docs/instalar-en-celular.md)**

## Arquitectura

| Componente | Tecnología | Uso |
|------------|------------|-----|
| API + web | FastAPI, SQLAlchemy, Jinja | Login web, `/api/v1/*` para el APK |
| Base de datos | PostgreSQL 16 (Docker) | Emails y hashes bcrypt |
| Android (Samsung) | Flet → `flet build apk` | Cliente en `client/` |
| iOS | Safari PWA | Misma URL `/login` del servidor |

## Requisitos

- Python 3.11+
- Docker y Docker Compose (PostgreSQL local)
- Para APK: Flutter SDK + JDK (ver guía Flet)

## Puesta en marcha

```bash
cp .env.example .env
# SESSION_SECRET (≥32 chars) + GYMVE_USER_*_PASSWORD_HASH (4 usuarios)

docker compose up -d

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python scripts/init_db.py
python scripts/seed_users.py

uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Web: [http://127.0.0.1:8000/login](http://127.0.0.1:8000/login)

### Generar hash bcrypt

```bash
python scripts/hash_password.py
```

**No guardes contraseñas en texto plano en el repositorio.** Solo hashes en `.env` (gitignored) o variables de despliegue.

### API (cliente Flet)

```text
POST /api/v1/login   {"email","password"}  → access_token
GET  /api/v1/me      Authorization: Bearer …
```

## Cliente Android (Flet)

```bash
pip install -r client/requirements.txt
cd client
export GYMVE_API_BASE_URL=http://192.168.1.XX:8000   # opcional en dev
flet run .                    # prueba en escritorio
flet build apk -v             # APK sideload (Samsung, sin Play Store)
```

En el Samsung, indica la **URL del API** en la pantalla de login (IP LAN o túnel HTTPS).

## Estructura

```text
app/              Backend FastAPI + plantillas web
client/           App Flet (APK)
scripts/          init_db, seed_users, hash_password
docker-compose.yml
docs/
mobile/           Legacy Expo (deprecated)
index.html        Legacy formulario En Manada
```

## Calidad

```bash
pip install ruff
ruff check app scripts client/main.py
```

## Variables de entorno

Ver [.env.example](.env.example): `DATABASE_URL`, `SESSION_SECRET`, usuarios para seed.

Licencia: uso privado familiar.
