import pytest

from app.core.rate_limit import _ip_para_limite, get_rate_limit_key
from tests.conftest import PASSWORD, crear_api_key, crear_usuario, token_para

LOGIN = "/auth/seguridad/login"


def login(client, email="usuario@example.com", password=PASSWORD, ip="203.0.113.1"):
    return client.post(
        LOGIN,
        json={"email": email, "password": password, "client_type": "api"},
        headers={"X-Forwarded-For": ip},
    )


def test_login_limita_a_5_por_minuto_por_ip(client):
    for _ in range(5):
        assert login(client, email="nadie@example.com").status_code == 401

    response = login(client, email="nadie@example.com")

    assert response.status_code == 429
    assert "Retry-After" in response.headers


def test_login_el_limite_es_por_ip(client):
    for _ in range(5):
        login(client, email="nadie@example.com", ip="203.0.113.1")

    assert login(client, email="nadie@example.com", ip="203.0.113.2").status_code == 401


def test_login_bloquea_la_cuenta_tras_10_fallos_desde_ips_distintas(client, db, tenant):
    crear_usuario(db, tenant=tenant)
    for i in range(10):
        login(client, password="incorrecta", ip=f"203.0.113.{i}")

    # Con la clave correcta y una IP nueva sigue bloqueada
    response = login(client, ip="198.51.100.1")

    assert response.status_code == 429
    assert "cuenta" in response.json()["error"]["message"]


def test_login_correcto_reinicia_los_fallos(client, db, tenant):
    crear_usuario(db, tenant=tenant)
    for i in range(9):
        login(client, password="incorrecta", ip=f"203.0.113.{i}")

    assert login(client, ip="198.51.100.1").status_code == 200
    for i in range(9):
        login(client, password="incorrecta", ip=f"192.0.2.{i}")

    assert login(client, ip="198.51.100.2").status_code == 200


@pytest.mark.parametrize("ip,esperado", [
    ("203.0.113.7", "203.0.113.7"),
    ("::ffff:203.0.113.7", "203.0.113.7"),
    ("2001:db8:1:2:aaaa::1", "2001-db8-1-2--_64"),
    ("2001:db8:1:2:bbbb::9", "2001-db8-1-2--_64"),
    ("testclient", "testclient"),
])
def test_ip_para_limite(ip, esperado):
    assert _ip_para_limite(ip) == esperado


class RequestFalso:
    def __init__(self, headers=None, cookies=None):
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.client = type("Cliente", (), {"host": "203.0.113.9"})()
        self.state = type("Estado", (), {})()


def test_identidad_jwt_valido(db, tenant):
    user = crear_usuario(db, tenant=tenant)
    request = RequestFalso(headers={"Authorization": f"Bearer {token_para(user)}"})
    assert get_rate_limit_key(request) == f"user:{user.id}"


def test_identidad_jwt_inventado_cuenta_por_ip():
    request = RequestFalso(headers={"Authorization": "Bearer inventado"})
    assert get_rate_limit_key(request) == "ip:203.0.113.9"


def test_identidad_api_key_activa(engine, db, tenant):
    prefix = crear_api_key(db, tenant).split(".")[0]
    request = RequestFalso(headers={"X-API-Key": f"{prefix}.cualquier-cosa"})
    assert get_rate_limit_key(request) == f"apikey:{prefix}"


def test_identidad_api_key_inventada_cuenta_por_ip(engine):
    request = RequestFalso(headers={"X-API-Key": "erp_inventado.secreto"})
    assert get_rate_limit_key(request) == "ip:203.0.113.9"
