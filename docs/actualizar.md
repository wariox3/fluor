# Script de actualización en el servidor

Guía para crear y dejar listo en el servidor el script `/root/actualizar_fluor.sh`, que actualiza **Semántica ERP API** con un solo comando en **Ubuntu 24.04 LTS**. El script hace los pasos del [procedimiento de actualización](despliegue.md#8-procedimiento-de-actualización) para no tener que escribirlos a mano cada vez.

## Tabla de contenido

- [Requisitos](#requisitos)
- [1. Crear el script](#1-crear-el-script)
- [2. Dar permisos](#2-dar-permisos)
- [3. Probarlo](#3-probarlo)
- [Cómo usarlo](#cómo-usarlo)
- [Qué hace el script](#qué-hace-el-script)
- [Si algo falla](#si-algo-falla)

---

## Requisitos

El servidor debe estar instalado según [despliegue.md](despliegue.md). En concreto:

- El código clonado en `/opt/fluor` y con propietario `fluor`.
- El entorno virtual en `/opt/fluor/.venv`.
- El servicio `fluor` creado en systemd y escuchando en `127.0.0.1:8010`.
- Acceso al servidor con un usuario que pueda usar `sudo`.
- `curl` instalado (viene en Ubuntu; si falta: `sudo apt install -y curl`).

Compruébalo rápido:

```bash
sudo -u fluor git -C /opt/fluor status
systemctl status fluor --no-pager
curl -fsS http://127.0.0.1:8010/health
```

---

## 1. Crear el script

Abre el archivo con un editor:

```bash
sudo nano /root/actualizar_fluor.sh
```

Pega este contenido:

```bash
#!/bin/bash
# Actualiza Semántica ERP API (Fluor) en producción.
# Uso: sudo /root/actualizar_fluor.sh

set -euo pipefail

APP_DIR="/opt/fluor"
SERVICE="fluor"
HEALTH_URL="http://127.0.0.1:8010/health"

# Ejecuta un comando como el usuario fluor
como_fluor() {
    sudo -u fluor "$@"
}

if [ "$(id -u)" -ne 0 ]; then
    echo "Ejecuta el script como root: sudo $0"
    exit 1
fi

cd "$APP_DIR"

echo ">> Descargando cambios..."
como_fluor git fetch origin

NUEVOS=$(como_fluor git log --oneline HEAD..origin/main)
if [ -z "$NUEVOS" ]; then
    echo "No hay cambios nuevos. Nada que actualizar."
    exit 0
fi

echo ">> Commits que entran:"
echo "$NUEVOS"

echo ">> Actualizando código..."
como_fluor git -c advice.detachedHead=false checkout --detach origin/main

echo ">> Instalando dependencias..."
como_fluor .venv/bin/pip install -r requirements.txt

echo ">> Aplicando migraciones..."
como_fluor .venv/bin/alembic upgrade head

echo ">> Reiniciando servicio..."
systemctl restart "$SERVICE"

echo ">> Verificando (hasta 60 segundos)..."
for i in $(seq 1 12); do
    sleep 5
    if curl -fsS "$HEALTH_URL"; then
        echo
        break
    fi
    if [ "$i" -eq 12 ]; then
        echo "El servicio no respondió. Revisa: journalctl -u $SERVICE -n 50"
        exit 1
    fi
    echo "   Aún no responde, reintentando ($i/12)..."
done

echo ">> Actualización completada: $(como_fluor git log -1 --oneline)"
```

Guarda con `Ctrl+O`, `Enter` y sal con `Ctrl+X`.

> Si pegaste el contenido desde Windows, quita los saltos de línea de Windows para evitar el error `/bin/bash^M: bad interpreter: No such file or directory`:
>
> ```bash
> sudo sed -i 's/\r$//' /root/actualizar_fluor.sh
> ```

---

## 2. Dar permisos

El script corre como root, así que solo root debe poder leerlo, modificarlo y ejecutarlo:

```bash
sudo chown root:root /root/actualizar_fluor.sh
sudo chmod 700 /root/actualizar_fluor.sh
```

Comprueba:

```bash
sudo ls -l /root/actualizar_fluor.sh
# -rwx------ 1 root root ... /root/actualizar_fluor.sh
```

---

## 3. Probarlo

1. Revisa que no tenga errores de sintaxis:

   ```bash
   sudo bash -n /root/actualizar_fluor.sh && echo "Sintaxis OK"
   ```

2. Ejecútalo cuando `main` no tenga cambios nuevos. Debe descargar, no encontrar commits y terminar sin tocar nada:

   ```
   >> Descargando cambios...
   No hay cambios nuevos. Nada que actualizar.
   ```

3. La primera actualización real hazla en un horario de poco tráfico y revisa la salida completa.

---

## Cómo usarlo

Cada vez que haya cambios en `main` para subir a producción:

```bash
sudo /root/actualizar_fluor.sh
```

No recibe argumentos: siempre despliega lo último de `origin/main`.

Antes de ejecutarlo:

- Si hay cambios en tablas de tenant, aplica el SQL primero ([sección 10](despliegue.md#10-cambios-en-las-bases-de-tenant)).
- Si hay migraciones que borran o renombran columnas, revisa que sean [compatibles](despliegue.md#migraciones-compatibles).
- No debe haber archivos modificados en `/opt/fluor`; si los hay, `git checkout` falla.

Salida de una actualización correcta:

```
>> Descargando cambios...
>> Commits que entran:
3453acd feat: add /dia endpoint ...
>> Actualizando código...
>> Instalando dependencias...
>> Aplicando migraciones...
>> Reiniciando servicio...
>> Verificando (hasta 60 segundos)...
{"status":"ok","database":"ok"}
>> Actualización completada: 3453acd feat: add /dia endpoint ...
```

---

## Qué hace el script

1. **Entra a la carpeta** `/opt/fluor`.
2. **Descarga los cambios** (`git fetch`).
3. **Muestra los commits que entran.** Si no hay ninguno, avisa y termina.
4. **Cambia el código** a `origin/main` (`git checkout`).
5. **Instala dependencias** (`pip install -r requirements.txt`).
6. **Aplica migraciones** de la Master DB (`alembic upgrade head`).
7. **Reinicia el servicio** (`systemctl restart fluor`).
8. **Verifica** que `/health` responda. Reintenta cada 5 segundos durante 1 minuto, porque los workers tardan en arrancar.

Aunque el script corre como root, `git`, `pip` y `alembic` se ejecutan como el usuario `fluor` (`sudo -u fluor`). Así los archivos de `/opt/fluor` siguen perteneciendo a `fluor` y git no rechaza el repositorio por ser de otro usuario. Solo el reinicio del servicio se hace como root.

---

## Si algo falla

El script usa `set -e`: **se detiene en el primer comando que falle** y no sigue con los demás. No revierte nada por su cuenta.

| Dónde falla | Qué pasa | Qué hacer |
|-------------|----------|-----------|
| Pasos 2 a 6 | El servicio **no se reinició**: sigue corriendo la versión anterior | Corrige el error y vuelve a ejecutar el script |
| Paso 7 u 8 | La versión nueva no arrancó bien | Revisa `journalctl -u fluor -n 50` y, si hace falta, sigue el [rollback](despliegue.md#9-rollback) |

Errores comunes:

| Error | Causa | Solución |
|-------|-------|----------|
| `Ejecuta el script como root` | Se ejecutó sin `sudo` | `sudo /root/actualizar_fluor.sh` |
| `Permission denied` | Faltan permisos de ejecución | Repite el [paso 2](#2-dar-permisos) |
| `/bin/bash^M: bad interpreter` | Saltos de línea de Windows | `sudo sed -i 's/\r$//' /root/actualizar_fluor.sh` |
| `Your local changes ... would be overwritten by checkout` | Alguien editó archivos en `/opt/fluor` | Revisa `sudo -u fluor git -C /opt/fluor status` y descarta o sube esos cambios por el repositorio |
| `curl: (7) Failed to connect` o `El servicio no respondió` | El servicio no arrancó, sigue arrancando o escucha en otro puerto | Ver [el servicio no responde](#el-servicio-no-responde) |

### El servicio no responde

`curl: (7) Failed to connect to 127.0.0.1 port 8010` significa que nada está escuchando en ese puerto. Revisa en este orden:

1. **¿El servicio está corriendo?**

   ```bash
   systemctl status fluor --no-pager
   ```

   Si dice `activating (auto-restart)` o `failed`, la app se cae al arrancar. Mira el error:

   ```bash
   journalctl -u fluor -n 50 --no-pager
   ```

   Causas típicas: falta una variable en `/opt/fluor/.env`, falla la conexión a MySQL o falta una dependencia (`ModuleNotFoundError`).

2. **¿Escucha en el puerto 8010?**

   ```bash
   sudo ss -ltnp | grep -E 'uvicorn|python|8010'
   ```

   Si aparece en otro puerto, el `ExecStart` de `/etc/systemd/system/fluor.service` usa un puerto distinto. Cambia `HEALTH_URL` en el script para que coincida.

3. **¿La app arranca a mano?** Muestra el error completo sin pasar por systemd:

   ```bash
   cd /opt/fluor && sudo -u fluor .venv/bin/python -c "import app.main"
   ```

Cuando el servicio responda con `curl -fsS http://127.0.0.1:8010/health`, vuelve a ejecutar el script.
