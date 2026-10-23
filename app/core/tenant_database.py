import re
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker, Session
from decouple import config
from fastapi import Depends, HTTPException, Request, status
from app.core.security import get_current_user
from app.core.master_database import get_master_db
from sqlalchemy.orm import declarative_base
from threading import Lock

VALID_DB_NAME = re.compile(r"^[a-zA-Z0-9_]+$")

Base = declarative_base()
tenant_engines = {}
tenant_lock = Lock()

DB_HOST = config("DB_HOST")
DB_PORT = config("DB_PORT", default="3306")
DB_USER = config("DB_USER")
DB_PASSWORD = config("DB_PASSWORD")

def get_tenant_engine(database_name: str):
    if not VALID_DB_NAME.match(database_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nombre de base de datos no válido"
        )

    if database_name in tenant_engines:
        return tenant_engines[database_name]

    with tenant_lock:
        if database_name in tenant_engines:
            return tenant_engines[database_name]

        DATABASE_URL = (
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
            f"@{DB_HOST}:{DB_PORT}/{database_name}"
        )

        # NullPool: sin pool por tenant. Con muchas bases accedidas de forma
        # esporádica, un QueuePool dejaría pool_size conexiones idle (Sleep) vivas
        # por cada tenant indefinidamente. NullPool abre la conexión por request y
        # la cierra de verdad en db.close(), evitando conexiones colgadas en MySQL.
        engine = create_engine(
            DATABASE_URL,
            poolclass=NullPool,
        )
        tenant_engines[database_name] = engine
        return engine


def get_tenant_db(request: Request, current_user: dict = Depends(get_current_user), master_db: Session = Depends(get_master_db),):
    from app.modules.mas.models.tenant import Tenant
    from app.modules.mas.models.user_tenant import UserTenant

    sub = current_user.get("sub", "")

    if sub.lstrip("-").isdigit():
        # JWT: la empresa sale del encabezado X-Tenant-ID, validada contra user_tenant
        tenant_header = request.headers.get("X-Tenant-ID", "").strip()
        if not tenant_header:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe indicar la empresa en el encabezado X-Tenant-ID",
            )
        if not tenant_header.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El encabezado X-Tenant-ID no es válido",
            )

        # Se consulta en cada petición para reflejar al instante accesos retirados
        tenant = (
            master_db.query(Tenant)
            .join(UserTenant, UserTenant.tenant_id == Tenant.id)
            .filter(
                UserTenant.usuario_id == int(sub),
                UserTenant.tenant_id == int(tenant_header),
                UserTenant.activo == True,
            )
            .first()
        )
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a esta empresa",
            )
        schema = tenant.schema
    else:
        # API Key: sub es el prefix — usamos tenant_id del payload para obtener el schema
        tenant_id = current_user.get("tenant_id")
        tenant = master_db.query(Tenant).filter(Tenant.id == tenant_id).first() if tenant_id else None
        schema = tenant.schema if tenant else None

    if not schema:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no tiene tenant asignado"
        )

    engine = get_tenant_engine(schema)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()