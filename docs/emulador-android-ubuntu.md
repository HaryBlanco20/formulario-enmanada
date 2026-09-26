# Emulador Android en Ubuntu (Samsung / dev)

Esta guía es para probar el **APK Flet (Samsung)** desde un **PC Ubuntu**.  
**iPhone no usa emulador Android:** en el mismo proyecto pruebas iOS con **Safari en un iPhone real** + URL **HTTPS** (ver [instalar-en-celular.md](instalar-en-celular.md)).

---

## Qué puedes probar en Ubuntu

| Objetivo | Herramienta |
|----------|-------------|
| App Android (GymVe APK) | Emulador Android + `adb` |
| Backend API | Docker Postgres + `uvicorn` en el host |
| Cliente iPhone | **No** en emulador — iPhone físico + túnel o HTTPS local |

**Simulador iOS:** solo en **macOS con Xcode**. Desde Ubuntu, no hay atajo oficial.

---

## Requisitos (Ubuntu)

1. **KVM** (aceleración hardware): usuario en grupo `kvm`, virtualización activa en BIOS.
2. **Android SDK** (cmdline-tools, platform-tools, emulator, imagen del sistema).
3. **JDK** + **Flutter** (Flet empaqueta con Flutter para `flet build apk`).

### KVM rápido

```bash
sudo apt install -y qemu-kvm libvirt-daemon-system
sudo usermod -aG kvm "$USER"
# Cierra sesión y vuelve a entrar
egrep -c '(vmx|svm)' /proc/cpuinfo   # >0 si CPU lo soporta
```

### Android SDK (resumen)

```bash
sudo apt install -y openjdk-17-jdk unzip
mkdir -p "$HOME/Android/Sdk/cmdline-tools"
# Descarga commandlinetools-linux desde developer.android.com/studio#command-line-tools-only
# Descomprime en $HOME/Android/Sdk/cmdline-tools/latest/

export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$PATH"

yes | sdkmanager --licenses
sdkmanager "platform-tools" "emulator" "platforms;android-34" "system-images;android-34;google_apis;x86_64"
avdmanager create avd -n Pixel_7_API_34 -k "system-images;android-34;google_apis;x86_64" -d pixel_7
```

Añade a `~/.bashrc`:

```bash
export ANDROID_HOME=$HOME/Android/Sdk
export ANDROID_AVD=Pixel_7_API_34
```

---

## Arrancar emulador + backend

**Terminal 1 — infra:**

```bash
cd gymve
make dev-up
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 — emulador:**

```bash
./scripts/run-android-emulator.sh
```

---

## URL del API (Samsung en emulador vs iPhone)

| Cliente | URL recomendada |
|---------|-------------------|
| **Emulador Android** | `http://10.0.2.2:8000` (mapeo al host) — solo dev; preferir HTTPS en builds reales |
| **HTTPS local (ambos)** | `https://gymve.local` con Caddy (`make dev-proxy`) + certificado mkcert |
| **iPhone (Safari)** | Misma URL HTTPS que el backend exponga (túnel o `gymve.local` si el iPhone confía el cert) |

Cleartext HTTP en Android 9+ está **restringido** por defecto. El flujo seguro por defecto del proyecto es **HTTPS** (Caddy o túnel). HTTP a `10.0.2.2` queda documentado solo para depuración rápida en emulador.

### HTTPS local con mkcert (opcional)

```bash
sudo apt install -y mkcert
mkcert -install
mkdir -p docker/caddy/certs
mkcert -cert-file docker/caddy/certs/gymve.local.pem -key-file docker/caddy/certs/gymve.local-key.pem gymve.local
echo "127.0.0.1 gymve.local" | sudo tee -a /etc/hosts
docker compose --profile proxy up -d
```

En el **iPhone**, instala el CA de mkcert o usa un **túnel público HTTPS** (más simple para familiares).

---

## Build e instalar APK

```bash
export GYMVE_API_BASE_URL=https://gymve.local   # o tu túnel
./scripts/build-and-install-apk.sh
```

O desarrollo en caliente (escritorio/emulador con Flet):

```bash
cd client
export GYMVE_API_BASE_URL=http://10.0.2.2:8000
flet run -d android   # si tu Flet soporta target android con dispositivo conectado
```

---

## Probar iPhone desde el mismo PC Ubuntu

1. Levanta backend + **HTTPS** (túnel Cloudflare o Caddy accesible en LAN).
2. En el iPhone: Safari → `https://…/login` → **Añadir a pantalla de inicio**.
3. Ajusta `CORS_ORIGINS` en `.env` a esa URL.

No necesitas adb ni emulador para iPhone.

---

## Scripts del repo

| Script | Uso |
|--------|-----|
| `scripts/run-android-emulator.sh` | Inicia `ANDROID_AVD` |
| `scripts/build-and-install-apk.sh` | `flet build apk` + `adb install -r` |
| `scripts/dev-up.sh` | Postgres + init + seed |

Más seguridad: [seguridad.md](seguridad.md).
