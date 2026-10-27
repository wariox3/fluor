import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine

from app.core import tenant_database
from app.core.tenant_database import get_tenant_db, get_tenant_engine
from tests.conftest import asociar_tenant, crear_api_key, crear_tenant, crear_usuario


@pytest.fixture
def schemas_abiertos(monkeypatch):
    """Registra qué base de tenant abre get_tenant_db, sin conectarse a MySQL."""
    abiertos = []

    def engine_falso(schema):
        abiertos.append(schema)
        return create_engine("sqlite://")

    monkeypatch.setattr(tenant_database, "get_tenant_engine", engine_falso)
    return abiertos


class RequestFalso:
    def __init__(self, tenant_id=None):
        self.headers = {"X-Tenant-ID": str(tenant_id)} if tenant_id is not None else {}


def abrir_tenant_db(current_user, master_db, tenant_id=None):
    generador = get_tenant_db(request=RequestFalso(tenant_id), current_user=current_user, master_db=master_db)
    next(generador)
    generador.close()


def codigo_error(current_user, master_db, tenant_id=None):
    with pytest.raises(HTTPException) as error:
        abrir_tenant_db(current_user, master_db, tenant_id)
    return error.value.status_code


def test_jwt_abre_la_empresa_del_header(db, schemas_abiertos):
    tenant_a = crear_tenant(db, "Empresa A", "empresa_a")
    user = crear_usuario(db, tenant=tenant_a)

    abrir_tenant_db({"sub": str(user.id)}, db, tenant_a.id)

    assert schemas_abiertos == ["empresa_a"]


def test_jwt_con_varias_empresas_abre_la_que_pide(db, schemas_abiertos):
    tenant_a = crear_tenant(db, "Empresa A", "empresa_a")
    tenant_b = crear_tenant(db, "Empresa B", "empresa_b")
    user = crear_usuario(db, tenant=tenant_a)
    asociar_tenant(db, user, tenant_b)

    abrir_tenant_db({"sub": str(user.id)}, db, tenant_b.id)
    abrir_tenant_db({"sub": str(user.id)}, db, tenant_a.id)

    assert schemas_abiertos == ["empresa_b", "empresa_a"]


def test_jwt_sin_header(db, schemas_abiertos):
    user = crear_usuario(db, tenant=crear_tenant(db, "Empresa A", "empresa_a"))

    assert codigo_error({"sub": str(user.id)}, db) == 400
    assert schemas_abiertos == []


def test_jwt_header_no_numerico(db, schemas_abiertos):
    user = crear_usuario(db, tenant=crear_tenant(db, "Empresa A", "empresa_a"))

    assert codigo_error({"sub": str(user.id)}, db, "1 OR 1=1") == 400
    assert schemas_abiertos == []


def test_jwt_empresa_sin_acceso(db, schemas_abiertos):
    crear_tenant(db, "Empresa A", "empresa_a")
    tenant_b = crear_tenant(db, "Empresa B", "empresa_b")
    user = crear_usuario(db, tenant=None)

    assert codigo_error({"sub": str(user.id)}, db, tenant_b.id) == 403
    assert schemas_abiertos == []


def test_jwt_acceso_inactivo(db, schemas_abiertos):
    tenant_a = crear_tenant(db, "Empresa A", "empresa_a")
    user = crear_usuario(db)
    acceso = asociar_tenant(db, user, tenant_a)

    abrir_tenant_db({"sub": str(user.id)}, db, tenant_a.id)
    # Retirar el acceso aplica de inmediato, sin esperar a que venza el token
    acceso.activo = False
    db.commit()

    assert codigo_error({"sub": str(user.id)}, db, tenant_a.id) == 403
    assert schemas_abiertos == ["empresa_a"]


def test_usuario_inexistente(db, schemas_abiertos):
    tenant_a = crear_tenant(db, "Empresa A", "empresa_a")

    assert codigo_error({"sub": "999"}, db, tenant_a.id) == 403


def test_api_key_abre_su_empresa_e_ignora_el_header(db, schemas_abiertos):
    tenant_a = crear_tenant(db, "Empresa A", "empresa_a")
    tenant_b = crear_tenant(db, "Empresa B", "empresa_b")
    prefix = crear_api_key(db, tenant_b).split(".")[0]

    abrir_tenant_db({"sub": prefix, "tenant_id": tenant_b.id}, db, tenant_a.id)

    assert schemas_abiertos == ["empresa_b"]


@pytest.mark.parametrize("nombre", [
    "empresa_a; DROP DATABASE master",
    "empresa_a`",
    "../empresa_a",
    "empresa-a",
    "",
])
def test_get_tenant_engine_rechaza_nombres_invalidos(nombre):
    with pytest.raises(HTTPException) as error:
        get_tenant_engine(nombre)

    assert error.value.status_code == 400
    assert nombre not in tenant_database.tenant_engines


def test_tenant_con_schema_invalido_no_abre_conexion(db):
    tenant = crear_tenant(db, "Empresa mala", "mala;DROP")
    user = crear_usuario(db, tenant=tenant)

    assert codigo_error({"sub": str(user.id)}, db, tenant.id) == 400
