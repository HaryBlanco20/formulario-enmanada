# Instalar GymVe en el celular (Samsung + iPhone)

GymVe es **privado** (sin App Store ni Play Store). Mismo backend **FastAPI + PostgreSQL** para la familia:

| Dispositivo | Cliente | Cómo “instalar” |
|-------------|---------|------------------|
| **Samsung (Android)** | APK **Flet** | Sideload del `.apk` + URL del API |
| **iPhone (iOS)** | **Safari / PWA** | No hay APK; añadir a pantalla de inicio |

Desde un **PC Ubuntu** puedes desarrollar y probar **Samsung** con emulador o APK real; para **iPhone** la vía práctica es un **iPhone físico en la misma red** (o túnel HTTPS), no el simulador iOS (solo en Mac).

---

## 1. Backend (obligatorio para ambos)

En tu PC Ubuntu (o mini servidor):

```bash
cd gymve
cp .env.example .env
# Define POSTGRES_*, GYMVE_APP_DB_*, SESSION_SECRET (≥32), hashes de los 4 usuarios

make dev-up
# o: ./scripts/dev-up.sh

source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Comprueba: `http://127.0.0.1:8000/health` → `{"status":"ok"}`.

### HTTPS (recomendado para iPhone y APK en red real)

iOS exige **HTTPS** para PWA fiable fuera de localhost. Android también conviene HTTPS (cleartext bloqueado por defecto).

Opciones (elige una):

1. **Túnel** (rápido, iPhone + Samsung): `cloudflared tunnel --url http://localhost:8000` → URL `https://….trycloudflare.com`
2. **Caddy local** (dev en Ubuntu): `make dev-proxy` tras generar certs en `docker/caddy/certs/` (ver [seguridad.md](seguridad.md))

Configura `CORS_ORIGINS` en `.env` con la URL HTTPS que uses (Samsung APK + Safari iPhone).

### Contraseñas (4 cuentas)

- Mínimo **10 caracteres** y un **carácter especial**.
- Solo **hashes bcrypt** en `.env`: `python scripts/hash_password.py` → `GYMVE_USER_N_PASSWORD_HASH` → `python scripts/seed_users.py`.

---

## 2. Instalar en dispositivos (Samsung + iPhone)

### 2.1 Samsung — APK sideload

**Construir APK (Ubuntu):**

```bash
source .venv/bin/activate
pip install -r client/requirements.txt
cd client
flet build apk -v
# o desde la raíz: ./scripts/build-and-install-apk.sh
```

**URL del API en la app** (pantalla de login):

| Escenario | URL típica |
|-----------|------------|
| PC y Samsung en la misma Wi‑Fi | `https://<túnel>` o `http://192.168.x.x:8000` (HTTP solo si el APK lo permite) |
| Emulador Android en el PC | `http://10.0.2.2:8000` (host) o `https://gymve.local` con certificado confiable |
| Producción / fuera de casa | **HTTPS** obligatorio (túnel o dominio propio) |

**Instalar sin Play Store:** copia el `.apk` al teléfono → Instalar → permitir fuentes desconocidas si Android lo pide.

**USB (opcional):** `adb install -r client/build/apk/*.apk`

Guía emulador en Ubuntu: [emulador-android-ubuntu.md](emulador-android-ubuntu.md).

### 2.2 iPhone — Safari / PWA (no APK)

Apple **no permite** instalar un APK/Python empaquetado sin App Store y **Mac + Xcode**. Este proyecto usa **web/PWA**:

1. En el iPhone (Safari), abre la **misma URL HTTPS** que uses para la familia, p. ej. `https://….trycloudflare.com/login` o `https://gymve.local/login` (certificado confiable en el iPhone si es local).
2. Inicia sesión (misma política de contraseña que el APK).
3. **Compartir → Añadir a pantalla de inicio** → icono **GymVe**.

**Desde Ubuntu:** no hay simulador iOS usable. Prueba con **iPhone real** en Wi‑Fi + backend accesible (IP LAN con HTTPS difícil; **túnel HTTPS** es lo más simple).

| Samsung | iPhone |
|---------|--------|
| APK + URL API en la app | Safari + `/login` + “Añadir a inicio” |
| Emulador opcional en Ubuntu | Solo dispositivo real (desde PC Ubuntu) |

---

## 3. Resumen de URLs

| Cliente | Qué configurar |
|---------|----------------|
| Samsung (APK) | Campo “URL del servidor API” → base HTTPS (sin `/login`) |
| iPhone (PWA) | Navegar a `{base}/login` |
| Backend | `DATABASE_URL`, `SESSION_SECRET`, `CORS_ORIGINS` |

La app Flet guarda la URL en almacenamiento del cliente (`client_storage`); **no** guarda contraseñas. Ver [seguridad.md](seguridad.md).

---

## 4. Acceso desde fuera de casa (ambos dispositivos)

```bash
cloudflared tunnel --url http://localhost:8000
```

Usa la URL `https://….trycloudflare.com`:

- **iPhone:** Safari → `/login` → pantalla de inicio.
- **Samsung:** misma URL base en el APK.

Actualiza `CORS_ORIGINS` si cambias de dominio.

---

## 5. Solución de problemas

| Síntoma | Revisar |
|---------|---------|
| iPhone no guarda PWA / cookies raras | Usar **HTTPS**, no HTTP en LAN |
| APK “no conecta” | URL API, firewall puerto 8000, preferir HTTPS |
| Login rechazado | Política de contraseña; `seed_users.py` |
| 429 demasiados intentos | Rate limit en login; esperar 1 minuto |

¿Postgres? `docker compose ps` y `make dev-up`.
