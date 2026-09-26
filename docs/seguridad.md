# Seguridad GymVe

App **privada** (4 usuarios). Clientes: **Samsung (APK + JWT)** e **iPhone (PWA + cookies de sesión)** sobre el mismo backend.

---

## Secretos y entorno

| Variable | Uso |
|----------|-----|
| `SESSION_SECRET` | Cookies web (iPhone PWA), base de JWT si no hay `JWT_SECRET` |
| `JWT_SECRET` | Opcional; tokens Bearer del APK |
| `POSTGRES_PASSWORD` | Superusuario Postgres (solo contenedor) |
| `GYMVE_APP_DB_PASSWORD` | Usuario SQL de aplicación (privilegios mínimos) |

- **Nunca** subas `.env` al repositorio.
- Rota secretos si hubo exposición: nuevo `SESSION_SECRET` invalida sesiones y tokens existentes.
- Generación: `openssl rand -base64 48`.

### Modo producción

Con `GYMVE_ENV=production`:

- Rechaza `SESSION_SECRET` / `JWT_SECRET` débiles o de ejemplo.
- Rechaza `CORS_ORIGINS=*`.
- Rechaza `GYMVE_ALLOW_INSECURE_DEV`.
- Cookies de sesión: `https_only=True`.

En **desarrollo**, `CORS_ORIGINS=*` sigue permitido; no uses eso en un servidor expuesto a Internet.

Comprobación local:

```bash
./scripts/security-check.sh
```

---

## Autenticación y contraseñas

- Política **servidor** (web, `/api/v1/login` y verificación bcrypt): ≥10 caracteres + carácter especial.
- **Rate limiting** en login web y API (`GYMVE_LOGIN_RATE_LIMIT`, default `10/minute`).
- Respuestas genéricas en fallo de login (no revelar si el email existe).

---

## CORS y HTTPS (Samsung + iPhone)

Configura orígenes explícitos en producción, por ejemplo:

```env
CORS_ORIGINS=https://tu-tunel.trycloudflare.com,https://gymve.local
```

- **iPhone PWA:** mismo origen que `/login` y `/static/*`.
- **APK Samsung:** peticiones API cross-origin al dominio HTTPS del backend; debe estar listado en `CORS_ORIGINS` si el navegador/WebView aplica CORS (httpx en Flet usa cliente nativo; CORS aplica sobre todo a la PWA).

**HTTPS:**

- Preferido: túnel (Cloudflare) o Caddy con certificados locales (`docker compose --profile proxy`).
- **HSTS** se envía cuando la petición es HTTPS o en producción (`SecurityHeadersMiddleware`).

Headers: `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Content-Security-Policy` razonable para PWA estática.

---

## PostgreSQL (Docker)

- Volumen nombrado `gymve_pgdata`.
- Script `docker/postgres/init-app-user.sh` crea `gymve_app` en la **primera** inicialización del volumen.
- `DATABASE_URL` debe usar `gymve_app`, no el superusuario.

Rotación de password DB: cambiar en `.env`, `ALTER USER` en Postgres, reiniciar API.

---

## Cliente Flet (Samsung)

- URL API en `client_storage` (`gymve_api_base`); token JWT en `gymve_token`.
- **No** se registran contraseñas en logs.
- Preferir `GYMVE_API_BASE_URL=https://…` en builds; evitar HTTP cleartext salvo emulador (`10.0.2.2`) en dev.

---

## Flags solo desarrollo

| Flag | Efecto |
|------|--------|
| `GYMVE_ALLOW_INSECURE_DEV` | Documentado para relajaciones futuras; **bloqueado** si `GYMVE_ENV=production` |
| `GYMVE_SESSION_HTTPS_ONLY=0` | Por defecto en dev; pon `1` al probar HTTPS local |

No desactives auth ni rate limits en producción.

---

## Checklist producción

1. `GYMVE_ENV=production`
2. Secretos aleatorios ≥32 caracteres
3. `CORS_ORIGINS` con URLs HTTPS reales
4. HTTPS terminado (Caddy, reverse proxy, o túnel)
5. `./scripts/security-check.sh` en CI o antes de desplegar
6. Firewall: exponer solo lo necesario
7. Backups del volumen Postgres

Esquema DB: [schema-versioning.md](schema-versioning.md).
