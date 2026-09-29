import os

# Las variables del entorno tienen prioridad sobre el .env en python-decouple: se fijan
# antes de importar la app para que las pruebas nunca toquen MySQL, Redis ni Sentry reales.
os.environ.update({
    "SECRET_KEY": "clave-de-pruebas",
    "DEBUG": "false",
    "ENVIRONMENT": "test",
    "SENTRY_DSN": "",
    "REDIS_URL": "",
    "TURNSTILE_ENABLED": "false",
    "DB_HOST": "127.0.0.1",
    "DB_USER": "pruebas",
    "DB_PASSWORD": "pruebas",
    "DB_MASTER_HOST": "127.0.0.1",
    "DB_MASTER_USER": "pruebas",
    "DB_MASTER_PASSWORD": "pruebas",
    "DB_MASTER_NAME": "pruebas",
})

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import master_database, rate_limit
from app.core.master_database import Base, _set_db_timezone, get_master_db
from app.core.rate_limit import limiter
from app.core.security import create_access_token, generate_api_key, hash_api_key, hash_password
from app.main import app
from app.modules.auth.models.api_key import ApiKey
from app.modules.auth.models.tenant import Tenant
from app.modules.auth.models.user import User, UserRole

# El listener de zona horaria ejecuta SQL de MySQL en cada conexión; SQLite no lo entiende
event.remove(Engine, "connect", _set_db_timezone)

PASSWORD = "Clave-Segura-123"


@pytest.fixture
def engine(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Rutas que abren la Master DB sin pasar por get_master_db
    monkeypatch.setattr("app.main.master_engine", engine)
    monkeypatch.setattr(master_database, "SessionLocal", TestingSession)
    monkeypatch.setattr(rate_limit, "SessionLocal", TestingSession)
    # Obliga a recargar los prefijos de API keys desde la base de cada prueba
    monkeypatch.setattr(rate_limit, "_prefijos_cargados_en", 0.0)
    monkeypatch.setattr(rate_limit, "_prefijos_activos", frozenset())

    yield engine
    engine.dispose()


@pytest.fixture
def db(engine):
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    yield session
    session.close()


@pytest.fixture
def client(engine):
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_master_db():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_master_db] = override_get_master_db
    limiter.reset()
    # https para que el cliente reenvíe las cookies marcadas como secure
    with TestClient(app, base_url="https://testserver") as test_client:
        yield test_client
    app.dependency_overrides.clear()
    limiter.reset()


@pytest.fixture
def tenant(db):
    return crear_tenant(db, "Empresa A", "empresa_a")


def crear_tenant(db, nombre, schema):
    tenant = Tenant(nombre=nombre, schema=schema, activo=True)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


def crear_usuario(db, email="usuario@example.com", role=UserRole.user, tenant=None, **campos):
    campos.setdefault("is_verified", True)
    user = User(
        email=email,
        password_hash=hash_password(PASSWORD),
        role=role,
        tenant_id=tenant.id if tenant else None,
        **campos,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def crear_api_key(db, tenant, **campos):
    prefix, api_key = generate_api_key()
    key = ApiKey(name="pruebas", prefix=prefix, key_hash=hash_api_key(api_key), tenant_id=tenant.id, **campos)
    db.add(key)
    db.commit()
    return api_key


def token_para(user):
    return create_access_token({
        "sub": str(user.id),
        "tenant_id": user.tenant_id,
        "role": user.role.value,
        "empleado_id": user.empleado_id,
    })


def auth_header(user):
    return {"Authorization": f"Bearer {token_para(user)}"}
