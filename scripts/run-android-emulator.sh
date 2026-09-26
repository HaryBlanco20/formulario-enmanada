#!/usr/bin/env bash
# Best-effort: inicia un AVD si ANDROID_AVD y Android SDK están configurados.
set -euo pipefail

SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-$HOME/Android/Sdk}}"
AVD="${ANDROID_AVD:-}"

if [[ ! -d "$SDK" ]]; then
  echo "No se encontró Android SDK en ANDROID_HOME/ANDROID_SDK_ROOT ($SDK)."
  echo "Ver docs/emulador-android-ubuntu.md"
  exit 1
fi

export PATH="$SDK/emulator:$SDK/platform-tools:$SDK/cmdline-tools/latest/bin:$PATH"

if ! command -v emulator >/dev/null 2>&1; then
  echo "Falta el binario 'emulator'. Instala Android Emulator via sdkmanager."
  exit 1
fi

if [[ -z "$AVD" ]]; then
  echo "Define ANDROID_AVD (nombre del dispositivo virtual)."
  echo "AVDs disponibles:"
  avdmanager list avd 2>/dev/null || emulator -list-avds
  exit 1
fi

echo "Iniciando emulador '$AVD' (Ctrl+C para salir)..."
exec emulator -avd "$AVD" -netdelay none -netspeed full
