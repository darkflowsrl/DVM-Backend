#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Uso: $0 <version_front> <version_back>"
    exit 1
fi

VERSION_FRONT=$1
VERSION_BACK=$2

nmcli dev wifi connect "dvm" password "dvm"
if [ $? -ne 0 ]; then
    echo "Error al conectar a la red Wi-Fi"
    exit 1
fi

BACKUP_DIR="/backups/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r /root/* "$BACKUP_DIR"
if [ $? -ne 0 ]; then
    echo "Error al hacer el backup de /root"
    exit 1
fi

find /root -name "*.AppImage" -type f -delete
if [ $? -ne 0 ]; then
    echo "Error al eliminar los archivos .AppImage"
    exit 1
fi

wget -O "/root/dvm-app-front-$VERSION_FRONT.AppImage" "https://github.com/SegarraFacundo/DVM-front/releases/download/v$VERSION_FRONT/dvm-app-front-$VERSION_FRONT.AppImage"
if [ $? -ne 0 ]; then
    echo "Error al descargar el archivo AppImage"
    exit 1
fi

chmod +x "/root/dvm-app-front-$VERSION_FRONT.AppImage"
if [ $? -ne 0 ]; then
    echo "Error al asignar permisos de ejecución al archivo AppImage"
    exit 1
fi

cd /root/Darkflow-HMI-Backend || exit 1
git pull
if [ $? -ne 0 ]; then
    echo "Error al hacer git pull en /root/Darkflow-HMI-Backend"
    exit 1
fi

BASHRC="/root/.bashrc"
NEW_LINE="startx /root/dvm-app-front-$VERSION_FRONT.AppImage --no-sandbox -- -nocursor"

if grep -q "startx /root/dvm-app-front-.*.AppImage --no-sandbox -- -nocursor" "$BASHRC"; then
    sed -i "s|startx /root/dvm-app-front-.*.AppImage --no-sandbox -- -nocursor|$NEW_LINE|" "$BASHRC"
else
    echo "$NEW_LINE" >> "$BASHRC"
fi

if [ $? -ne 0 ]; then
    echo "Error al actualizar el archivo .bashrc."
    exit 1
fi

echo "Archivo .bashrc actualizado exitosamente."

reboot
