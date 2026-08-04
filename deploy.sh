#!/usr/bin/env bash
# _*_ ENCODING: UTF-8 _*_
#
# Despliegue de Fluor en produccion.
# Uso: ./deploy.sh

set -euo pipefail

APP_DIR="/root/aplicaciones/fluor"
VENV="$HOME/.venvs/fluor/bin/activate"
SERVICE="fluor"
LOCK_FILE="/tmp/fluor-deploy.lock"

log() {
    printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1"
}

# Evita despliegues concurrentes (p. ej. si el script se dispara dos veces por error)
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
    log "Ya hay un despliegue en curso. Abortando."
    exit 1
fi

cd "$APP_DIR"
# shellcheck source=/dev/null
source "$VENV"

PREVIOUS_COMMIT="$(git rev-parse HEAD)"

# Si algo falla a partir de aqui, garantizamos que el servicio quede arriba
# (con el codigo anterior si hubo rollback, o con el nuevo si el fallo fue posterior).
service_up_on_exit() {
    local exit_code=$?
    if [ "$exit_code" -ne 0 ]; then
        log "Fallo detectado (exit $exit_code). Verificando estado del servicio..."
    fi
    if ! systemctl is-active --quiet "$SERVICE"; then
        log "Servicio caido, reiniciando ${SERVICE}..."
        service "$SERVICE" start
    fi
    exit "$exit_code"
}
trap service_up_on_exit EXIT

log "Descargando cambios..."
git fetch origin main
git merge --ff-only origin/main

NEW_COMMIT="$(git rev-parse HEAD)"
if [ "$PREVIOUS_COMMIT" = "$NEW_COMMIT" ]; then
    log "No hay cambios nuevos en main. Nada que desplegar."
    exit 0
fi
log "Actualizando de ${PREVIOUS_COMMIT:0:7} a ${NEW_COMMIT:0:7}"

log "Deteniendo servicio..."
service "$SERVICE" stop

log "Aplicando migraciones..."
if ! alembic upgrade head; then
    log "ERROR: migracion fallida. Revirtiendo codigo a ${PREVIOUS_COMMIT:0:7}..."
    git reset --hard "$PREVIOUS_COMMIT"
    log "Codigo revertido. El servicio se reiniciara con la version anterior."
    exit 1
fi

log "Iniciando servicio..."
service "$SERVICE" start

# Pequeña espera y verificacion de que el proceso sigue vivo tras el arranque
sleep 2
if ! systemctl is-active --quiet "$SERVICE"; then
    log "ERROR: el servicio no quedo activo tras el despliegue."
    exit 1
fi

log "Despliegue completado correctamente (commit ${NEW_COMMIT:0:7})."
