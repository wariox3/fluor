# Despliegue en producción

Guía para instalar y actualizar **Semántica ERP API** en un servidor Linux. Está escrita para Ubuntu 24.04 LTS; en otra distribución cambian los nombres de los paquetes, pero el procedimiento es el mismo.

## Tabla de contenido

- [Arquitectura de producción](#arquitectura-de-producción)
- [1. Preparación del servidor (una sola vez)](#1-preparación-del-servidor-una-sola-vez)
- [2. Base de datos](#2-base-de-datos)
- [3. Instalación del código](#3-instalación-del-código)
- [4. Variables de entorno](#4-variables-de-entorno)
- [5. Servicio systemd](#5-servicio-systemd)
- [6. Nginx y HTTPS](#6-nginx-y-https)
- [7. Primer despliegue](#7-primer-despliegue)
- [8. Procedimiento de actualización](#8-procedimiento-de-actualización)
- [9. Rollback](#9-rollback)
- [10. Cambios en las bases de tenant](#10-cambios-en-las-bases-de-tenant)
- [11. Operación: logs, monitoreo y backups](#11-operación-logs-monitoreo-y-backups)
- [12. Checklist de seguridad](#12-checklist-de-seguridad)
- [Limitaciones conocidas](#limitaciones-conocidas)

---

## Arquitectura de producción

```
Internet ──443──▶ Nginx (TLS, proxy inverso)
                    │  http://127.0.0.1:8010
                    ▼
                 systemd: fluor.service
                 uvicorn (N workers)
                    │  cada worker tiene su subproceso de PDF (WeasyPrint)
                    ▼
                 MySQL ─ Master DB (bdfluor) + una base por tenant
                    │
                 Servicios externos: Backblaze B2, Sentry, Turnstile, Zinc
```

Principios:

- La aplicación **nunca corre como root**; usa el usuario de sistema `fluor`.
- Uvicorn solo escucha en `127.0.0.1`; el único punto de entrada público es Nginx.
- MySQL **no se expone** a Internet.
- El código es un clon del repositorio en `/opt/fluor`. Actualizar es mover el clon a otro commit; un rollback es volver al commit anterior.
- Los secretos viven en `/opt/fluor/.env`, que está en `.gitignore` y nunca se sube al repositorio.

---

## 1. Preparación del servidor (una sola vez)

### Paquetes del sistema

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
    git python3.12 python3.12-venv python3-dev build-essential \
    libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 \
    libmagic1 fonts-liberation fontconfig \
    nginx certbot python3-certbot-nginx \
    mysql-client ufw
```

| Paquete | Motivo |
|---------|--------|
| `libpango-*`, `libharfbuzz-subset0` | Librerías nativas que necesita WeasyPrint para generar PDF |
| `libmagic1` | La usa `python-magic` para detectar el tipo de archivo en `doc/fichero` |
| `fonts-liberation` | Fuentes con las mismas métricas que Arial (las plantillas PDF usan `Arial, sans-serif`) |
| `mysql-client` | Cliente `mysql` para aplicar scripts SQL a los tenants ([sección 10](#10-cambios-en-las-bases-de-tenant)) |

### Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

No abras el puerto 8010 ni el 3306.

### Usuario de la aplicación

```bash
sudo adduser --system --group --home /opt/fluor --shell /usr/sbin/nologin fluor
```

Los despliegues se hacen como `fluor` con `sudo -u fluor ...`. Solo reiniciar el servicio necesita `sudo`.

---

## 2. Base de datos

Si MySQL corre en otro servidor, limita su acceso a la IP privada del servidor de la aplicación.

### Usuarios de MySQL

Crea usuarios dedicados; **no uses `root`** en producción.

```sql
-- Master DB (Alembic necesita permisos DDL)
CREATE DATABASE bdfluor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'fluor_master'@'10.0.0.%' IDENTIFIED BY '<contraseña-larga>';
GRANT ALL PRIVILEGES ON bdfluor.* TO 'fluor_master'@'10.0.0.%';

-- Tenants: permisos DML sobre las bases de las empresas
CREATE USER 'fluor_tenant'@'10.0.0.%' IDENTIFIED BY '<otra-contraseña-larga>';
GRANT SELECT, INSERT, UPDATE, DELETE ON `empresa_%`.* TO 'fluor_tenant'@'10.0.0.%';
```

> Ajusta el host (`10.0.0.%`) y el patrón de nombres de las bases de tenant a tu entorno. Las bases de tenant se crean y modifican fuera de la aplicación (ver [sección 10](#10-cambios-en-las-bases-de-tenant)), por lo que el usuario de tenant no necesita permisos DDL.

### Conexiones

Cada worker de uvicorn abre su propio pool contra la Master DB: hasta `DB_MASTER_POOL_SIZE + DB_MASTER_MAX_OVERFLOW` conexiones (30 por defecto). Las bases de tenant usan `NullPool`, así que abren una conexión por petición.

Comprueba que `max_connections` en MySQL cubre al menos:

```
workers × (DB_MASTER_POOL_SIZE + DB_MASTER_MAX_OVERFLOW) + peticiones concurrentes a tenants + margen
```

La zona horaria de cada conexión la fija la aplicación (`DB_TIME_ZONE`, `-05:00` por defecto), así que no depende de la configuración del servidor MySQL.

---

## 3. Instalación del código

```
/opt/fluor/                 # clon del repositorio (propietario fluor)
├── app/
├── migrations_master/
├── requirements.txt
├── .venv/                  # entorno virtual (ignorado por git)
└── .env                    # secretos, chmod 600 (ignorado por git)
```

```bash
# /opt pertenece a root: crea la carpeta con sudo y dásela a fluor
sudo install -d -o fluor -g fluor -m 750 /opt/fluor

# Clonar (la carpeta debe estar vacía)
sudo -u fluor git clone https://github.com/wariox3/fluor.git /opt/fluor

# Entorno virtual
sudo -u fluor python3.12 -m venv /opt/fluor/.venv
sudo -u fluor /opt/fluor/.venv/bin/pip install --upgrade pip
sudo -u fluor /opt/fluor/.venv/bin/pip install -r /opt/fluor/requirements.txt
```

El repositorio es público, así que el clon por HTTPS no necesita credenciales. Si pasa a ser privado, no uses credenciales personales: registra en GitHub una **deploy key de solo lectura** (clave SSH del usuario `fluor`) y cambia la URL a SSH:

```bash
sudo -u fluor git -C /opt/fluor remote set-url origin git@github.com:wariox3/fluor.git
```

Como `/opt/fluor` también es el home de `fluor`, ahí aparecerá la caché de pip. Exclúyela de git para que `git status` quede limpio:

```bash
sudo -u fluor sh -c 'printf ".cache/\n" >> /opt/fluor/.git/info/exclude'
```

> **No edites archivos en el servidor.** Cualquier cambio local en `/opt/fluor` bloquea las actualizaciones. Todo cambio entra por el repositorio.

---

## 4. Variables de entorno

Crea `/opt/fluor/.env`:

```bash
sudo -u fluor install -m 600 /dev/null /opt/fluor/.env
sudo -u fluor nano /opt/fluor/.env
```

```env
# ── General ─────────────────────────────────────────────
DEBUG=False
ENVIRONMENT=production
# Generar con: python3 -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=
APP_URL=https://semanticaapi.com.co

# ── Master DB ───────────────────────────────────────────
DB_MASTER_HOST=
DB_MASTER_PORT=3306
DB_MASTER_USER=fluor_master
DB_MASTER_PASSWORD=
DB_MASTER_NAME=bdfluor
DB_MASTER_POOL_SIZE=10
DB_MASTER_MAX_OVERFLOW=20
DB_MASTER_POOL_TIMEOUT=30

# ── Tenant DB ───────────────────────────────────────────
DB_HOST=
DB_PORT=3306
DB_USER=fluor_tenant
DB_PASSWORD=
DB_TIME_ZONE=-05:00

# ── Backblaze B2 (módulo doc) ───────────────────────────
B2_KEY_ID=
B2_APPLICATION_KEY=
B2_BUCKET_NAME=

# ── Seguridad / integraciones ───────────────────────────
TURNSTILE_ENABLED=True
TURNSTILE_SECRET_KEY=
ZINC_URL=

# ── Observabilidad ──────────────────────────────────────
SENTRY_DSN=
SENTRY_TRACES_SAMPLE_RATE=0.0

# ── Generación de PDF ───────────────────────────────────
PDF_WORKER_MAX_TASKS=50
PDF_RENDER_TIMEOUT=60
```

| Variable | Obligatoria | Nota |
|----------|:-----------:|------|
| `SECRET_KEY` | ✅ | Si cambia, se invalidan todos los JWT emitidos. Guárdala también en el gestor de secretos del equipo. |
| `DEBUG` | ✅ | **Siempre `False`**: con `True` las respuestas de error exponen detalles internos. |
| `DB_MASTER_*`, `DB_*` | ✅ | |
| `SENTRY_DSN` | Recomendada | Vacía = Sentry desactivado. |
| `TURNSTILE_*` | Recomendada | Protección anti-bots en login/registro. |
| `B2_*` | Si se usa `doc` | |

`python-decouple` lo encuentra en la raíz del proyecto, igual que en desarrollo.

---

## 5. Servicio systemd

`/etc/systemd/system/fluor.service`:

```ini
[Unit]
Description=Semantica ERP API (Fluor)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=fluor
Group=fluor
WorkingDirectory=/opt/fluor
ExecStart=/opt/fluor/.venv/bin/uvicorn app.main:app \
    --host 127.0.0.1 --port 8010 \
    --workers 4 \
    --proxy-headers --forwarded-allow-ips 127.0.0.1 \
    --no-server-header \
    --timeout-graceful-shutdown 30
Restart=always
RestartSec=5
KillSignal=SIGTERM
TimeoutStopSec=40

# Hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=true
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable fluor
```

**Número de workers:** empieza con un worker por vCPU y ajusta según la memoria. Cada worker carga la aplicación completa y levanta su propio subproceso de WeasyPrint cuando genera un PDF, así que vigila la RAM (`systemctl status fluor` muestra el consumo total).

Para que el usuario `fluor` pueda reiniciar el servicio sin tener sudo completo, crea `/etc/sudoers.d/fluor` con `visudo -f /etc/sudoers.d/fluor`:

```
fluor ALL=(root) NOPASSWD: /usr/bin/systemctl restart fluor, /usr/bin/systemctl status fluor
```

---

## 6. Nginx y HTTPS

`/etc/nginx/sites-available/fluor`:

```nginx
upstream fluor_api {
    server 127.0.0.1:8010;
    keepalive 32;
}

server {
    listen 80;
    server_name api.semanticaapi.com.co;
    # certbot añade aquí la redirección a HTTPS y el bloque 443
    
    client_max_body_size 25m;          # subida de documentos (doc/fichero, formato_imagen)

    location / {
        proxy_pass http://fluor_api;
        proxy_http_version 1.1;
        proxy_set_header Connection "";

        proxy_set_header Host              $host;
        # IMPORTANTE: sobrescribir (no concatenar) X-Forwarded-For.
        # El rate limit usa el primer valor de este header; si se concatena,
        # un cliente puede falsificar su IP y evadir los límites.
        proxy_set_header X-Forwarded-For   $remote_addr;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_read_timeout 90s;            # > PDF_RENDER_TIMEOUT
        proxy_send_timeout 90s;
    }

    location = /health {
        proxy_pass http://fluor_api;
        access_log off;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/fluor /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# Certificado TLS (renovación automática vía systemd timer de certbot)
sudo certbot --nginx -d api.semanticaapi.com.co --redirect
sudo certbot renew --dry-run
```

Las cookies de sesión se emiten con `Secure` y `SameSite=None`, así que **HTTPS es obligatorio** para que funcione el login web.

---

## 7. Primer despliegue

1. Completa las secciones 1 a 6.
2. Comprueba que la app importa con la configuración real:

   ```bash
   cd /opt/fluor && sudo -u fluor .venv/bin/python -c "import app.main"
   ```

3. Aplica las migraciones de la Master DB:

   ```bash
   cd /opt/fluor && sudo -u fluor .venv/bin/alembic upgrade head
   ```

4. Arranca el servicio: `sudo systemctl start fluor`.
5. Verifica: `curl -fsS https://api.semanticaapi.com.co/health` → `{"status":"ok","database":"ok"}`.

> Ejecuta siempre `alembic upgrade head` **antes** de arrancar la app. Al iniciar, la app ejecuta `create_all()` sobre la Master DB, que crea las tablas que falten pero no las registra en Alembic; si arranca primero, las migraciones posteriores pueden fallar porque la tabla ya existe.

---

## 8. Procedimiento de actualización

### Antes de desplegar

- [ ] El commit a desplegar está en `main` y fue revisado.
- [ ] Se leyeron las migraciones nuevas en `migrations_master/versions/`. ¿Alguna borra o renombra columnas? Ver [migraciones compatibles](#migraciones-compatibles).
- [ ] Si hay cambios en modelos de tenant, el SQL está preparado ([sección 10](#10-cambios-en-las-bases-de-tenant)).
- [ ] Si `requirements.txt` cambió, se revisó qué dependencias nuevas entran.
- [ ] Se eligió un horario de bajo tráfico si hay migraciones pesadas.
- [ ] Opcional: etiqueta la versión (`git tag v2026.09.17 && git push --tags`) para desplegar una referencia fija.

### Pasos

Ejecutar como `fluor` (`sudo -u fluor -s`):

```bash
set -euo pipefail
cd /opt/fluor
REF=origin/main                            # o un tag: v2026.09.17

# 1. Traer los cambios
test -z "$(git status --porcelain --untracked-files=no)"   # falla si hay cambios locales
git log -1 --oneline                       # commit actual, por si hay que volver
git fetch origin --tags --prune
git log --oneline HEAD.."$REF"             # revisa qué entra

# 2. Cambiar el código y actualizar dependencias
git -c advice.detachedHead=false checkout --detach "$REF"
.venv/bin/pip install -r requirements.txt

# 3. Comprobación: la app importa sin errores
.venv/bin/python -c "import app.main"

# 4. Migraciones
.venv/bin/alembic upgrade head

# 5. Reiniciar y verificar
sudo systemctl restart fluor
sleep 5
curl -fsS http://127.0.0.1:8010/health
journalctl -u fluor --since "2 min ago" --no-pager | tail -50
```

Haz los pasos 2 a 5 seguidos. Desde el `checkout` los archivos del disco ya son de la versión nueva, pero los workers siguen corriendo la anterior hasta el reinicio; cualquier módulo o plantilla que se cargue en ese intervalo (por ejemplo, el subproceso de PDF) puede mezclar versiones.

Si falla el paso 1, producción no se ha tocado. Si falla el 2, 3 o 4, ve al [rollback](#9-rollback) **antes** de reiniciar.

### Después de desplegar

- Prueba manualmente un flujo crítico: login, una consulta de tenant y la generación de un PDF.
- Revisa que Sentry no reciba errores nuevos durante los siguientes 15 minutos.
- Avisa al equipo qué commit o tag quedó en producción (`git -C /opt/fluor log -1 --oneline`).

### Migraciones compatibles

Entre el paso 4 y el reinicio, la versión anterior del código sigue corriendo contra la base ya migrada. Para que eso no rompa nada, las migraciones deben ser **compatibles con el código anterior** (patrón *expand / contract*):

- ✅ Agregar tablas, agregar columnas que acepten `NULL` o tengan valor por defecto, agregar índices.
- ❌ Borrar o renombrar columnas o tablas que el código actual todavía usa.

Para borrar o renombrar: primero despliega el código que ya no las usa y, **en un despliegue posterior**, la migración que las elimina.

Si un cambio no puede ser compatible, programa una ventana de mantenimiento: `sudo systemctl stop fluor`, haz los pasos 2 a 4 y arranca el servicio.

---

## 9. Rollback

### Solo código (no hubo migraciones, o son compatibles)

Como `fluor`:

```bash
cd /opt/fluor
git reflog -5                                  # confirma cuál era el commit anterior
PREV=$(git rev-parse --short 'HEAD@{1}')       # posición de HEAD antes del último checkout
git log -1 --oneline "$PREV" && echo "Volviendo a: $PREV"
git -c advice.detachedHead=false checkout --detach "$PREV"
.venv/bin/pip install -r requirements.txt
sudo systemctl restart fluor
curl -fsS http://127.0.0.1:8010/health
```

`pip install` reinstala las versiones del commit anterior, pero no desinstala paquetes que haya agregado la versión nueva; normalmente no molestan.

### Código y base de datos

1. Revierte la migración **antes** de volver al commit anterior: los archivos de la migración solo existen en la versión nueva.

   ```bash
   cd /opt/fluor && .venv/bin/alembic downgrade <revision-anterior>
   ```

2. Haz el rollback de código descrito arriba.

Si el `downgrade` no es viable (por ejemplo, la migración borró datos), la única salida es restaurar el último backup de la base ([sección 11](#backups)), perdiendo lo que se escribió después.

---

## 10. Cambios en las bases de tenant

Alembic **solo** gestiona la Master DB. La aplicación **no** crea ni modifica tablas en las bases de tenant (`create_all()` solo se ejecuta sobre la Master DB). Por lo tanto:

- Todo cambio en `app/modules/*/models/` que afecte a una tabla de tenant necesita un script SQL que se aplique **a cada base de tenant**.
- Aplica ese SQL **antes** de desplegar el código que lo necesita, respetando las mismas reglas de [compatibilidad](#migraciones-compatibles).
- Guarda los scripts versionados (por ejemplo `sql/tenant/2026-09-17_agregar_columna_x.sql`) para poder aplicarlos a tenants nuevos y saber cuáles ya se ejecutaron.

Ejemplo para aplicar un script a todos los tenants registrados:

```bash
for schema in $(mysql -N -h "$DB_MASTER_HOST" -u fluor_master -p bdfluor \
                  -e "SELECT \`schema\` FROM tenant WHERE activo = 1"); do
    echo ">> $schema"
    mysql -h "$DB_HOST" -u <usuario-ddl> -p "$schema" < sql/tenant/<script>.sql || break
done
```

> Los tenants están en la tabla `tenant` de la Master DB (modelo `app/modules/auth/models/tenant.py`). Usa un usuario con permisos DDL distinto del que usa la aplicación, y decide si también aplicas el script a los tenants inactivos.

---

## 11. Operación: logs, monitoreo y backups

### Logs

La aplicación escribe en stdout y systemd los guarda en journald.

```bash
journalctl -u fluor -f                         # en vivo
journalctl -u fluor --since "1 hour ago"
journalctl -u fluor -p err --since today       # solo errores
```

Limita cuánto espacio ocupan en `/etc/systemd/journald.conf` (`SystemMaxUse=1G`) y reinicia `systemd-journald`. Cada respuesta incluye el header `X-Request-ID`; pídele ese valor a quien reporte un error y búscalo en los logs y en Sentry.

Los logs de Nginx están en `/var/log/nginx/` y logrotate los rota automáticamente.

### Monitoreo

- **Uptime:** configura un monitor externo (UptimeRobot, Better Stack, etc.) contra `https://<dominio>/health`. Responde `200` si la app y la Master DB están bien, y `503` si la base no responde.
- **Errores:** Sentry con `SENTRY_DSN` y alertas por email o Slack para los errores nuevos.
- **Recursos:** vigila la RAM y el número de conexiones de MySQL (`SHOW STATUS LIKE 'Threads_connected';`).
- **Certificado TLS:** el monitor de uptime normalmente avisa cuando está por vencer.

### Backups

- Programa un `mysqldump --single-transaction` diario de la Master DB **y de todas las bases de tenant**, con retención (por ejemplo 7 diarios y 4 semanales).
- Guarda una copia **fuera del servidor** (por ejemplo, un bucket B2 distinto del de documentos).
- **Prueba la restauración** en otro entorno al menos una vez por trimestre. Un backup que nunca se ha restaurado no garantiza nada.
- Respalda también `/opt/fluor/.env` en el gestor de secretos del equipo.

---

## 12. Checklist de seguridad

- [ ] `DEBUG=False` y `ENVIRONMENT=production`.
- [ ] `SECRET_KEY` aleatoria de al menos 32 bytes, distinta a la de desarrollo.
- [ ] `.env` con permisos `600` y propietario `fluor`.
- [ ] Servicio corriendo como `fluor`, no como root.
- [ ] Uvicorn escuchando solo en `127.0.0.1`.
- [ ] Firewall: solo 22, 80 y 443 abiertos. MySQL no es accesible desde Internet.
- [ ] Usuarios de MySQL dedicados con permisos mínimos (nunca `root`).
- [ ] HTTPS con redirección desde HTTP y renovación automática probada.
- [ ] Nginx sobrescribe `X-Forwarded-For` con `$remote_addr`.
- [ ] `TURNSTILE_ENABLED=True` con su clave configurada.
- [ ] SSH solo con clave (`PasswordAuthentication no`) y actualizaciones de seguridad automáticas (`unattended-upgrades`).
- [ ] Revisar si `/docs`, `/redoc` y `/openapi.json` deben ser públicos en producción. Hoy lo son; se pueden bloquear en Nginx o desactivar en `FastAPI(...)`.
- [ ] Revisar la lista de orígenes CORS en `app/main.py`: incluye `http://localhost:4200`.

---

## Limitaciones conocidas

Aspectos del código actual que afectan a producción y conviene tener presentes:

| Tema | Detalle | Posible mejora |
|------|---------|----------------|
| Rate limit por worker | `slowapi` guarda los contadores en memoria, así que con N workers el límite real por IP puede llegar a N veces el configurado. | Usar Redis como almacenamiento (`Limiter(storage_uri="redis://...")`); `redis` ya está en `requirements.txt`. |
| IP del cliente | `get_client_ip` confía en el primer valor de `X-Forwarded-For`. | La configuración de Nginx de esta guía lo resuelve; no expongas uvicorn directamente. |
| Reinicio con corte breve | `systemctl restart` deja la API sin responder unos segundos mientras arrancan los workers, y Nginx devuelve `502` en ese intervalo. | Desplegar en horarios de bajo tráfico o, si hace falta cero interrupciones, usar dos instancias detrás del upstream y reiniciarlas por turnos. |
| Tenants sin migraciones | Los cambios de esquema en tenants son manuales ([sección 10](#10-cambios-en-las-bases-de-tenant)). | Adoptar una herramienta de migraciones por tenant. |
