# GymVe

<<<<<<< HEAD
Proyecto en blanco: empezamos desde cero.
=======
App móvil privada para uso familiar (iPhone y Android), **sin publicación** en App Store ni Google Play. Esta fase incluye solo **inicio de sesión** con correo y contraseña.

El código de la app está en [`mobile/`](mobile/).

## Stack

- [Expo](https://docs.expo.dev/) (React Native) + TypeScript
- [Supabase Auth](https://supabase.com/docs/guides/auth) — `signInWithPassword`, sesión persistente con AsyncStorage

## Requisitos

- Node.js 20+
- Cuenta en [Supabase](https://supabase.com/) (plan gratuito basta para 4 usuarios)
- Para probar en dispositivo: [Expo Go](https://expo.dev/go) (desarrollo) o builds internos (ver más abajo)

## Configuración de entorno

1. Crea un proyecto en Supabase.
2. En **Authentication → Providers**, deja activo **Email** (password).
3. Copia variables de **Project Settings → API**:

```bash
cd mobile
cp .env.example .env
# Edita .env con EXPO_PUBLIC_SUPABASE_URL y EXPO_PUBLIC_SUPABASE_ANON_KEY
```

4. (Opcional) Lista blanca de correos en `EXPO_PUBLIC_ALLOWED_EMAILS` (hasta 4, separados por coma).

## Política de contraseñas

Al crear usuarios en el panel de Supabase (o al validar en la app antes de enviar el formulario):

| Regla | Detalle |
|--------|---------|
| Longitud mínima | 10 caracteres |
| Carácter especial | Al menos uno que **no** sea letra ni dígito (p. ej. `!`, `@`, `#`, `$`) |

Expresión de referencia (TypeScript): ` /^(?=.*[^A-Za-z0-9]).{10,}$/ `

Mensajes en español en [`mobile/src/lib/passwordPolicy.ts`](mobile/src/lib/passwordPolicy.ts).

**No guardes contraseñas reales en el repositorio.** Defínelas solo en el dashboard de Supabase al crear cada usuario.

## Crear los 4 usuarios familiares

1. Supabase → **Authentication → Users → Add user → Create new user**.
2. Repite para cada miembro (4 cuentas): correo único + contraseña que cumpla la política.
3. Si usas confirmación de correo, desactívala para pruebas internas (**Authentication → Providers → Email**) o confirma cada usuario manualmente.
4. Opcional: pon los 4 correos en `EXPO_PUBLIC_ALLOWED_EMAILS` para bloquear otros inicios de sesión.

## Ejecutar en desarrollo

```bash
cd mobile
npm install
npx expo start
```

- Escanea el QR con **Expo Go** (Android / iOS).
- Asegúrate de que el `.env` esté en `mobile/` antes de arrancar (Expo lee `EXPO_PUBLIC_*` al iniciar).

Comprobación de tipos:

```bash
cd mobile && npm run typecheck
```

## Distribución sin tiendas públicas

| Plataforma | Enfoque recomendado |
|------------|---------------------|
| **Desarrollo** | Expo Go + `npx expo start` (misma red o túnel Expo) |
| **Android (Samsung, etc.)** | [EAS Build](https://docs.expo.dev/build/introduction/) → perfil **preview** o **internal** → instala el **APK** o enlace interno (no hace falta Play Store) |
| **iOS (iPhone)** | EAS Build con perfil **ad hoc** (UDIDs registrados) o **TestFlight** en modo interno (solo invitados, no listado público en App Store) |

Pasos generales EAS (cuando quieras builds):

```bash
cd mobile
npx eas-cli login
npx eas build:configure
npx eas build --platform android --profile preview
npx eas build --platform ios --profile preview
```

Documentación: [Internal distribution](https://docs.expo.dev/build/internal-distribution/), [Android APK](https://docs.expo.dev/build-reference/apk/), [iOS ad hoc](https://docs.expo.dev/build/internal-distribution/#ad-hoc-distribution).

## Otros archivos en el repo

- `index.html` — formulario legacy de otro proyecto (En Manada); no forma parte de GymVe.

## Próximos pasos (fuera de alcance actual)

Rutinas, progreso, perfiles — tras estabilizar login y builds internos.
>>>>>>> ed86b7b (feat(gymve): Expo login scaffold with Supabase Auth)
