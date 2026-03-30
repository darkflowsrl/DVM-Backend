#!/usr/bin/env bash
set -euo pipefail

# script that prepares the CAN interface and launches the FastAPI app.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

CAN_IFACE=can0
BITRATE=250000

SUDO=""
if [[ $(id -u) -ne 0 ]]; then
  if ! command -v sudo &>/dev/null; then
    echo "sudo no disponible: ejecutá este script como root." >&2
    exit 1
  fi
  SUDO=sudo
fi

configure_can_link() {
  echo "Limpiando interfaz $CAN_IFACE..."
  $SUDO ip link set "$CAN_IFACE" down || true
  echo "Configurando $CAN_IFACE a $BITRATE bps..."
  $SUDO ip link set "$CAN_IFACE" up type can bitrate "$BITRATE"
  echo "Estado actual:" 
  ip -details link show "$CAN_IFACE"
}

configure_can_link

echo "Ejecutando la API FastAPI..."
exec python3 main.py