#!/usr/bin/env bash
# Construye APK Flet (Samsung) e instala en dispositivo/emulador conectado por adb.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

API_HINT="${GYMVE_API_BASE_URL:-https://gymve.local}"
echo "Sugerencia URL API en el APK (emulador HTTP legacy: http://10.0.2.2:8000):"
echo "  $API_HINT"
echo "iPhone no usa APK — Safari PWA con la misma URL HTTPS del backend."
echo ""

if [[ -d .venv ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

pip install -q -r client/requirements.txt
cd client
flet build apk -v

APK="$(find build -name '*.apk' -type f 2>/dev/null | head -n1)"
if [[ -z "$APK" ]]; then
  echo "No se encontró APK en client/build/"
  exit 1
fi

SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-$HOME/Android/Sdk}}"
export PATH="$SDK/platform-tools:$PATH"

if ! command -v adb >/dev/null 2>&1; then
  echo "APK generado: client/$APK (adb no disponible para instalar)"
  exit 0
fi

adb wait-for-device
adb install -r "$APK"
echo "Instalado. Abre GymVe en el emulador/Samsung y configura la URL del API."
