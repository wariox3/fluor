from datetime import datetime, timedelta, timezone

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from jose import jwt

from app.core.config import ALGORITHM, SECRET_KEY
from app.core.master_database import get_master_db
from app.core.security import get_current_user
from app.modules.auth.models.user import UserRole
from tests.conftest import auth_header, crear_api_key, crear_usuario, token_para

ME = "/auth/seguridad/me"


@pytest.fixture
def api_key_client(client):
    """App mínima protegida solo con get_current_user, para probar la API key aislada."""
    from app.main import app

    mini = FastAPI()

    @mini.get("/protegida")
    def protegida(user: dict = Depends(get_current_user)):
        return user

    mini.dependency_overrides[get_master_db] = app.dependency_overrides[get_master_db]
    return TestClient(mini)


def test_sin_credenciales(client):
    assert client.get(ME).status_code == 401


@pytest.mark.xfail(strict=True, reason="http_exception_handler descarta los headers de la HTTPException")
def test_sin_credenciales_indica_www_authenticate(client):
    assert client.get(ME).headers.get("WWW-Authenticate") == "Bearer"


def test_bearer_valido(client, db, tenant):
    user = crear_usuario(db, tenant=tenant)
    response = client.get(ME, headers=auth_header(user))
    assert response.status_code == 200
    assert response.json()["email"] == user.email


def test_token_expirado(client, db, tenant):
    user = crear_usuario(db, tenant=tenant)
    vencido = jwt.encode(
        {"sub": str(user.id), "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        SECRET_KEY, algorithm=ALGORITHM,
    )
    assert client.get(ME, headers={"Authorization": f"Bearer {vencido}"}).status_code == 401


def test_token_con_otra_clave(client, db, tenant):
    user = crear_usuario(db, tenant=tenant)
    falso = jwt.encode({"sub": str(user.id)}, "otra-clave", algorithm=ALGORITHM)
    assert client.get(ME, headers={"Authorization": f"Bearer {falso}"}).status_code == 401


def test_token_sin_firma_alg_none(client, db, tenant):
    user = crear_usuario(db, tenant=tenant)
    # Encabezado {"alg":"none"} + payload sin firma
    header = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0"
    payload = token_para(user).split(".")[1]
    sin_firma = f"{header}.{payload}."
    assert client.get(ME, headers={"Authorization": f"Bearer {sin_firma}"}).status_code == 401


def test_cookie_access_token(client, db, tenant):
    user = crear_usuario(db, tenant=tenant)
    client.cookies.set("access_token", token_para(user))
    assert client.get(ME).status_code == 200


def test_api_key_valida(api_key_client, db, tenant):
    api_key = crear_api_key(db, tenant)
    response = api_key_client.get("/protegida", headers={"X-API-Key": api_key})
    assert response.status_code == 200
    assert response.json() == {"sub": api_key.split(".")[0], "tenant_id": tenant.id}


@pytest.mark.parametrize("valor", ["erp_noexiste.secreto", "sin-punto", ""])
def test_api_key_inexistente(api_key_client, valor):
    response = api_key_client.get("/protegida", headers={"X-API-Key": valor})
    assert response.status_code == 401


def test_api_key_con_secreto_incorrecto(api_key_client, db, tenant):
    prefix = crear_api_key(db, tenant).split(".")[0]
    response = api_key_client.get("/protegida", headers={"X-API-Key": f"{prefix}.secreto-incorrecto"})
    assert response.status_code == 401


def test_api_key_inactiva(api_key_client, db, tenant):
    api_key = crear_api_key(db, tenant, is_active=False)
    assert api_key_client.get("/protegida", headers={"X-API-Key": api_key}).status_code == 401


@pytest.mark.xfail(
    strict=True,
    raises=TypeError,
    reason="MySQL/SQLite devuelven expires_at sin zona horaria y se compara con un datetime aware",
)
def test_api_key_expirada(api_key_client, db, tenant):
    api_key = crear_api_key(db, tenant, expires_at=datetime.now(timezone.utc) - timedelta(days=1))
    response = api_key_client.get("/protegida", headers={"X-API-Key": api_key})
    assert response.status_code == 401


@pytest.mark.parametrize("role,esperado", [
    (UserRole.admin, 200),
    (UserRole.control, 403),
    (UserRole.user, 403),
    (UserRole.employee, 403),
])
def test_require_admin(client, db, tenant, role, esperado):
    user = crear_usuario(db, role=role, tenant=tenant)
    assert client.get("/auth/user/lista", headers=auth_header(user)).status_code == esperado


@pytest.mark.parametrize("role,esperado", [
    (UserRole.admin, 200),
    (UserRole.control, 200),
    (UserRole.user, 403),
    (UserRole.viewer, 403),
])
def test_require_admin_control(client, db, tenant, role, esperado):
    user = crear_usuario(db, role=role, tenant=tenant)
    assert client.get("/auth/api-key/lista", headers=auth_header(user)).status_code == esperado
