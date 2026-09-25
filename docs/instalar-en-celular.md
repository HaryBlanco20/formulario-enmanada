# Instalar GymVe en el celular (sin App Store ni Play Store)

GymVe usa **Python**: un **servidor API** (FastAPI + PostgreSQL) y, en **Samsung**, un **APK** hecho con **Flet**. En **iPhone** se usa la **web/PWA** en Safari (Apple no permite instalar APKs arbitrarios).

---

## 1. Servidor y base de datos (obligatorio)

En la computadora donde corre el backend (PC de casa, mini servidor, etc.):

```bash
cd gymve
cp .env.example .env
# Edita SESSION_SECRET y los 4 usuarios (hashes bcrypt)

docker compose up -d
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python scripts/init_db.py
python scripts/seed_users.py

uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Comprueba: `http://<IP-DE-TU-PC>:8000/health` debe responder `{"status":"ok"}`.

### Contraseñas de las 4 cuentas

- Mínimo **10 caracteres** y al menos un **carácter especial** (`!@#$%…`).
- En el repositorio solo van **hashes bcrypt**; genera uno con:

```bash
python scripts/hash_password.py
```

Pega el resultado en `GYMVE_USER_N_PASSWORD_HASH` en tu `.env` y vuelve a ejecutar `python scripts/seed_users.py`.

---

## 2. Samsung (Android) — APK sideload

### 2.1 Construir el APK (en tu PC)

Requisitos: Python 3.11+, [Flutter SDK](https://docs.flutter.dev/get-started/install) (Flet lo usa para empaquetar Android), Java JDK.

```bash
cd gymve
source .venv/bin/activate
pip install -r client/requirements.txt

cd client
flet build apk -v
```

El APK suele quedar en `client/build/apk/` (nombre tipo `app-release.apk`). Consulta la salida de `flet build` si la ruta cambia según la versión de Flet.

### 2.2 Configurar la URL del API en el teléfono

La app pide la **URL del servidor API** en la pantalla de login, por ejemplo:

| Dónde corre el API | URL típica en el Samsung |
|--------------------|---------------------------|
| PC en la misma Wi‑Fi | `http://192.168.1.XX:8000` (IP local del PC) |
| Emulador Android en el PC | `http://10.0.2.2:8000` |
| Servidor con túnel HTTPS | `https://tu-dominio.trycloudflare.com` |

**Importante:** Android 9+ bloquea HTTP claro por defecto. Para red local:

- Preferible un **túnel HTTPS** (Cloudflare Tunnel, ngrok), o
- Ajustar la política de red del APK en builds avanzados de Flet/Android (solo si sabes lo que haces).

Para prueba en casa con HTTP, algunos equipos permiten excepciones; si falla la conexión, usa túnel HTTPS.

### 2.3 Instalar el APK sin Play Store

1. Copia el `.apk` al Samsung (USB, Drive, Telegram, etc.).
2. Abre el archivo → **Instalar**.
3. Si Android pide permiso: **Ajustes → Seguridad → Instalar apps desconocidas** (o “Fuentes desconocidas”) para el navegador o **Mis archivos** que uses.
4. Abre **GymVe**, pon la URL del API, correo y contraseña.

#### Opcional: instalar por USB (adb)

Con [depuración USB](https://developer.android.com/studio/debug/dev-options) activada:

```bash
adb install -r client/build/apk/app-release.apk
```

---

## 3. iPhone (iOS) — Web / PWA (no APK)

No hay APK en iPhone. Usa **Safari**:

1. Asegúrate de que el API sea accesible (misma Wi‑Fi o **túnel HTTPS**; iOS exige HTTPS para muchas funciones PWA fuera de localhost).
2. Abre `https://…/login` (o `http://IP:8000/login` solo en LAN si Safari lo permite).
3. Inicia sesión.
4. **Compartir → Añadir a pantalla de inicio** → icono **GymVe**.

Limitación honesta: un **APK/Python nativo empaquetado para iOS** requiere **Mac + Xcode + cuenta Apple Developer**; este proyecto no publica en App Store, por eso la vía recomendada es **PWA en Safari**.

---

## 4. Acceso desde fuera de casa (túnel)

Ejemplo con Cloudflare Tunnel (gratis):

```bash
cloudflared tunnel --url http://localhost:8000
```

Usa la URL `https://….trycloudflare.com` en el Samsung (APK) o en el iPhone (Safari / pantalla de inicio).

---

## 5. Resumen rápido

| Dispositivo | Qué instalar | URL |
|-------------|--------------|-----|
| Samsung | APK Flet (`flet build apk`) | URL del API en pantalla de login |
| iPhone | PWA Safari | `/login` del servidor |
| Backend | Docker Postgres + uvicorn | `DATABASE_URL` en `.env` |

¿Problemas? Revisa que Postgres esté arriba (`docker compose ps`), que hayas hecho `seed_users.py`, y que el firewall del PC permita el puerto **8000** en la red local.
