# Semántica ERP API

API multi-tenant para un ERP empresarial, construida con **FastAPI**, **SQLAlchemy** y **MySQL**. Expone módulos de negocio independientes (RRHH, transporte, financiero, CRM, cartera, turismo, documentos) sobre una arquitectura de doble base de datos que aísla la información de cada empresa.

<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.135-009688?logo=fastapi&logoColor=white">
  <img alt="SQLAlchemy" src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00">
  <img alt="MySQL" src="https://img.shields.io/badge/MySQL-PyMySQL-4479A1?logo=mysql&logoColor=white">
</p>

---

## Tabla de contenido

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Módulos](#módulos)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración (`.env`)](#configuración-env)
- [Ejecución](#ejecución)
- [Migraciones](#migraciones)
- [Autenticación](#autenticación)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Agregar un módulo nuevo](#agregar-un-módulo-nuevo)

---

## Características

- 🏢 **Multi-tenant** — base de datos por empresa, resuelta dinámicamente desde el JWT.
- 🔐 **Doble autenticación** — JWT (OAuth2 Bearer / cookie) y API Keys con prefijo, hasheadas con argon2.
- 🧩 **Modular** — cada vertical de negocio vive en su propio paquete con router, modelos y schemas.
- 🛡️ **Rate limiting** — límites por IP vía `slowapi` (login y registro con límites más estrictos).
- 📄 **Almacenamiento de documentos** — integración con Backblaze B2.
- 🧾 **Generación de PDF** — etiquetas y reportes con WeasyPrint / ReportLab.
- 📊 **Observabilidad** — `X-Request-ID` por petición, manejo central de errores y reporte a Sentry.

---

## Arquitectura

### Patrón de doble base de datos

| Base | Módulo | Propósito |
|------|--------|-----------|
| **Master DB** | `app/core/master_database.py` | Base central compartida: usuarios, API keys y tenants. Toda operación de auth usa `get_master_db()`. |
| **Tenant DB** | `app/core/tenant_database.py` | Base por empresa, seleccionada en tiempo de petición desde el claim `tenant_schema` del JWT. Los engines se cachean en `tenant_engines` (thread-safe con `Lock`). Los nombres de base se validan contra `[a-zA-Z0-9_]` antes de usarse. |

- Las rutas con datos de empresa usan `Depends(get_tenant_db)`.
- Las rutas de auth o de módulos solo-master (p. ej. `mas`) usan `Depends(get_master_db)`.

### Cross-cutting concerns (`app/core/`)

- `config.py` — Settings cargados por `python-decouple`. JWT `HS256`, token de acceso 60 min, refresh 7 días.
- `security.py` — Hash de contraseñas (argon2), encode/decode de JWT, generación/verificación de API keys, dependencias de auth.
- `middleware.py` — `ErrorHandlingMiddleware`: añade `X-Request-ID`, captura excepciones no controladas y expone el detalle solo si `DEBUG=true`.
- `rate_limit.py` — Limiter de `slowapi`; por defecto 10 req/min por IP (login 5/min, registro 3/min).
- `backblaze.py` — Cliente thread-safe de Backblaze B2 con ciclo de refresco de token de 23 horas.
- `logging.py` — Configuración de logging de la librería estándar.

---

## Módulos

| Prefijo | Módulo | Descripción | Base |
|---------|--------|-------------|------|
| `/auth` | **auth** | Login, registro de usuarios y gestión de API keys | Master |
| `/rhu`  | **rhu** | Recurso Humano (`rhu_empleado`, `rhu_pago`) | Tenant |
| `/tte`  | **tte** | Transporte y Logística (`tte_guia` y relacionados) | Tenant |
| `/gen`  | **gen** | Utilidades generales: ciudades, ítems, terceros | Tenant |
| `/fin`  | **fin** | Financiero: rutas de balance | Tenant |
| `/doc`  | **doc** | Gestión documental sobre Backblaze B2 | Tenant |
| `/tur`  | **tur** | Turismo: agendamiento | Tenant |
| `/crm`  | **crm** | CRM: gestión de negocios/deals | Tenant |
| `/car`  | **car** | Cartera (cuentas por cobrar) | Tenant |
| `/mas`  | **mas** | Vertical master: datos cross-tenant (p. ej. `credito_solicitud`) | **Solo Master** |

---

## Requisitos

- **Python 3.12+**
- **MySQL** (acceso a la base master y a las bases por empresa)
- Cuenta de **Backblaze B2** (para el módulo de documentos)

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone <url-del-repo>
cd fluor

# 2. Crear y activar un entorno virtual
python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Crear el archivo .env (ver siguiente sección)
```

---

## Configuración (`.env`)

Crea un archivo `.env` en la raíz del proyecto:

```env
DEBUG=
SECRET_KEY=

# Tenant DB (por empresa, dinámica)
DB_HOST=
DB_PORT=
DB_USER=
DB_PASSWORD=

# Master DB (registro central de auth/usuarios)
DB_MASTER_HOST=
DB_MASTER_PORT=
DB_MASTER_USER=
DB_MASTER_PASSWORD=
DB_MASTER_NAME=
DB_MASTER_POOL_SIZE=10
DB_MASTER_MAX_OVERFLOW=20
DB_MASTER_POOL_TIMEOUT=30

# Backblaze B2 (almacenamiento de documentos)
B2_KEY_ID=
B2_APPLICATION_KEY=
B2_BUCKET_NAME=
```

---

## Ejecución

```bash
# Servidor de desarrollo (con recarga automática)
uvicorn app.main:app --reload
```

Una vez levantado, la documentación interactiva queda disponible en:

- **Swagger UI** → http://localhost:8000/docs
- **ReDoc** → http://localhost:8000/redoc

---

## Migraciones

Alembic está configurado **únicamente para la Master DB** (`migrations_master/`). Las tablas de las Tenant DB se crean automáticamente vía `Base.metadata.create_all()` al conectarse, por lo que **no requieren migración**.

```bash
# Aplicar migraciones a la Master DB
alembic -c alembic.ini upgrade head

# Generar una nueva migración (tras modificar modelos de la Master DB)
alembic -c alembic.ini revision --autogenerate -m "descripcion_del_cambio"
```

> Al añadir modelos a la Master DB, recuerda importarlos en `migrations_master/env.py`.

---

## Autenticación

Coexisten dos mecanismos:

1. **JWT (OAuth2 Bearer)** — Login vía `POST /auth/seguridad/login` con `client_type`. Si `client_type == "web"`, el token se devuelve como cookie `httponly`; en caso contrario, en el cuerpo de la respuesta. El payload contiene `sub` (id de usuario como string), `tenant_id`, `role` y `empleado_id`.
2. **API Key** — Claves con prefijo (`erp_<hex>.<secret>`) almacenadas hasheadas (argon2) en la Master DB. Se validan con el header `X-API-Key`.

`get_current_user()` resuelve la identidad en este orden: header OAuth2 Bearer → credenciales Bearer directas → header `X-API-Key` → cookie `access_token`.

> **Importante:** el id entero del usuario está en `current_user["sub"]` (es un *string*; conviértelo con `int(current_user["sub"])` cuando lo necesites como FK).

Helpers de rol disponibles en `app/core/security.py`: `require_admin()`, `require_admin_control()`.

---

## Estructura del proyecto

Cada módulo de negocio vive en `app/modules/<módulo>/` con esta organización:

```
app/
├── core/                  # Configuración, seguridad, BD, middleware, rate limit
│   ├── config.py
│   ├── security.py
│   ├── master_database.py
│   ├── tenant_database.py
│   ├── middleware.py
│   ├── rate_limit.py
│   ├── backblaze.py
│   └── logging.py
├── modules/
│   └── <módulo>/
│       ├── router.py      # Registra el APIRouter del módulo con su prefijo
│       ├── routes/        # Un archivo por recurso
│       ├── models/        # Modelos ORM de SQLAlchemy
│       └── schemas/       # Schemas Pydantic de request/response
└── main.py                # Punto de entrada: middlewares, CORS, routers
```

---

## Agregar un módulo nuevo

1. Crear `app/modules/<nombre>/` con los subdirectorios `router.py`, `routes/`, `models/` y `schemas/`.
2. Añadir el import wildcard en `app/main.py` (p. ej. `from app.modules.<nombre> import models`) para que SQLAlchemy registre los modelos.
3. Incluir el router en `app/main.py` con `app.include_router(...)`.
4. Usar `Depends(get_tenant_db)` para datos de empresa o `Depends(get_master_db)` para datos master.
5. Si los modelos pertenecen a la **Master DB**, importarlos en `migrations_master/env.py` y ejecutar `alembic revision --autogenerate`. Si son de Tenant DB, se crean automáticamente vía `create_all()` — sin migración.
