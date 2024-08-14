#!/bin/bash

BACKUP_DIR="/backups"

KEEP=2

NUM_BACKUPS=$(ls -1t "$BACKUP_DIR"/backup_* | wc -l)

if [ "$NUM_BACKUPS" -le "$KEEP" ]; then
    echo "No se eliminaron backups. Solo se encontraron $NUM_BACKUPS, que es menor o igual al límite de $KEEP."
    exit 0
fi

ls -1t "$BACKUP_DIR"/backup_* | tail -n +$(($KEEP + 1)) | xargs rm -rf

echo "Backups viejos eliminados, se mantuvieron los $KEEP más recientes."
