import time

import pytest

from app.core.security import decode_refresh_token, decode_token
from tests.conftest import PASSWORD, crear_usuario

LOGIN = "/auth/seguridad/login"


def login(client, email="usuario@example.com", password=PASSWORD, client_type="mobile"):
    return client.post(LOGIN, json={"email": email, "password": password, "client_type": client_type})


def test_login_mobile_devuelve_tokens_en_el_cuerpo(client, db, tenant):
    user = crear_usuario(db, tenant=tenant)

    response = login(client)

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["id"] == user.id
    payload = decode_token(body["access_token"])
    assert payload["sub"] == str(user.id)
    assert payload["role"] == "user"
    # La empresa no viaja en el token: se elige por petición con X-Tenant-ID
    assert "tenant_id" not in payload
    assert decode_refresh_token(body["refresh_token"])["sub"] == str(user.id)
    assert "access_token" not in response.cookies


def test_login_mobile_refresh_token_dura_30_dias(client, db, tenant):
    crear_usuario(db, tenant=tenant)

    body = login(client).json()

    payload = decode_refresh_token(body["refresh_token"])
    dias = (payload["exp"] - time.time()) / 86400
    assert 29.9 < dias <= 30


def test_login_mobile_refresca_con_el_token_en_el_cuerpo(client, db, tenant):
    user = crear_usuario(db, tenant=tenant)
    refresh_token = login(client).json()["refresh_token"]

    response = client.post("/auth/seguridad/refresh", json={"refresh_token": refresh_token})

    assert response.status_code == 200
    assert decode_token(response.json()["access_token"])["sub"] == str(user.id)
    assert "access_token" not in response.cookies


def test_login_rechaza_client_types_eliminados(client, db, tenant):
    crear_usuario(db, tenant=tenant)

    assert login(client, client_type="integration").status_code == 422


def test_login_api_devuelve_tokens_en_el_cuerpo_sin_turnstile(client, db, tenant):
    user = crear_usuario(db, tenant=tenant)

    response = login(client, client_type="api")

    assert response.status_code == 200
    body = response.json()
    assert decode_token(body["access_token"])["sub"] == str(user.id)
    payload = decode_refresh_token(body["refresh_token"])
    assert payload["sub"] == str(user.id)
    assert 29.9 < (payload["exp"] - time.time()) / 86400 <= 30
    assert "access_token" not in response.cookies


def test_login_web_devuelve_cookies_httponly(client, db, tenant):
    crear_usuario(db, tenant=tenant)

    response = login(client, client_type="web")

    assert response.status_code == 200
    assert "access_token" not in response.json()
    cookies = response.headers.get_list("set-cookie")
    access = next(c for c in cookies if c.startswith("access_token="))
    refresh = next(c for c in cookies if c.startswith("refresh_token="))
    for cookie in (access, refresh):
        assert "HttpOnly" in cookie
        assert "Secure" in cookie
        assert "SameSite=none" in cookie


def test_login_web_la_cookie_autentica_y_refresca(client, db, tenant):
    user = crear_usuario(db, tenant=tenant)
    login(client, client_type="web")

    me = client.get("/auth/seguridad/me")
    assert me.status_code == 200
    assert me.json()["id"] == user.id

    assert client.post("/auth/seguridad/refresh").status_code == 200


@pytest.mark.parametrize("email,password", [
    ("usuario@example.com", "clave-incorrecta"),
    ("no-existe@example.com", PASSWORD),
])
def test_login_credenciales_invalidas(client, db, tenant, email, password):
    crear_usuario(db, tenant=tenant)

    response = login(client, email=email, password=password)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_login_cuenta_no_verificada(client, db, tenant):
    crear_usuario(db, tenant=tenant, is_verified=False)

    response = login(client)

    assert response.status_code == 403
    assert response.json()["error"]["is_verified"] is False


def test_login_usuario_inactivo(client, db, tenant):
    crear_usuario(db, tenant=tenant, is_active=False)

    assert login(client).status_code == 403


def test_refresh_rechaza_un_access_token(client, db, tenant):
    crear_usuario(db, tenant=tenant)
    access_token = login(client).json()["access_token"]
    client.cookies.set("refresh_token", access_token)

    response = client.post("/auth/seguridad/refresh")

    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Token no es un refresh token"
