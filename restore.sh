#!/bin/bash

BACKUP_DIR="/backups"

LATEST_BACKUP=$(ls -td "$BACKUP_DIR"/backup_* | head -1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "No se encontró ningún backup para restaurar."
    exit 1
fi

echo "Restaurando desde el backup: $LATEST_BACKUP"

cp -r "$LATEST_BACKUP"/* /root/
if [ $? -ne 0 ]; then
    echo "Error al restaurar el backup."
    exit 1
fi

echo "Restauración completada exitosamente."
