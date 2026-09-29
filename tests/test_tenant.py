import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine

from app.core import tenant_database
from app.core.tenant_database import get_tenant_db, get_tenant_engine
from tests.conftest import crear_api_key, crear_tenant, crear_usuario


@pytest.fixture
def schemas_abiertos(monkeypatch):
    """Registra qué base de tenant abre get_tenant_db, sin conectarse a MySQL."""
    abiertos = []

    def engine_falso(schema):
        abiertos.append(schema)
        return create_engine("sqlite://")

    monkeypatch.setattr(tenant_database, "get_tenant_engine", engine_falso)
    return abiertos


def abrir_tenant_db(current_user, master_db):
    generador = get_tenant_db(current_user=current_user, master_db=master_db)
    next(generador)
    generador.close()


def test_jwt_abre_la_base_del_tenant_del_usuario(db, schemas_abiertos):
    tenant_a = crear_tenant(db, "Empresa A", "empresa_a")
    user = crear_usuario(db, tenant=tenant_a)

    abrir_tenant_db({"sub": str(user.id), "tenant_id": tenant_a.id}, db)

    assert schemas_abiertos == ["empresa_a"]


def test_jwt_ignora_el_tenant_id_del_token(db, schemas_abiertos):
    """El schema sale del usuario en la Master DB, no del claim tenant_id del token."""
    tenant_a = crear_tenant(db, "Empresa A", "empresa_a")
    tenant_b = crear_tenant(db, "Empresa B", "empresa_b")
    user = crear_usuario(db, tenant=tenant_a)

    abrir_tenant_db({"sub": str(user.id), "tenant_id": tenant_b.id}, db)

    assert schemas_abiertos == ["empresa_a"]


def test_jwt_refleja_cambio_de_tenant_sin_nuevo_token(db, schemas_abiertos):
    tenant_a = crear_tenant(db, "Empresa A", "empresa_a")
    tenant_b = crear_tenant(db, "Empresa B", "empresa_b")
    user = crear_usuario(db, tenant=tenant_a)
    token_viejo = {"sub": str(user.id), "tenant_id": tenant_a.id}

    user.tenant_id = tenant_b.id
    db.commit()
    abrir_tenant_db(token_viejo, db)

    assert schemas_abiertos == ["empresa_b"]


def test_usuario_sin_tenant(db, schemas_abiertos):
    user = crear_usuario(db)

    with pytest.raises(HTTPException) as error:
        abrir_tenant_db({"sub": str(user.id)}, db)

    assert error.value.status_code == 400
    assert schemas_abiertos == []


def test_usuario_inexistente(db, schemas_abiertos):
    with pytest.raises(HTTPException) as error:
        abrir_tenant_db({"sub": "999"}, db)

    assert error.value.status_code == 400


def test_api_key_abre_la_base_de_su_tenant(db, schemas_abiertos):
    tenant_b = crear_tenant(db, "Empresa B", "empresa_b")
    prefix = crear_api_key(db, tenant_b).split(".")[0]

    abrir_tenant_db({"sub": prefix, "tenant_id": tenant_b.id}, db)

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

    with pytest.raises(HTTPException) as error:
        abrir_tenant_db({"sub": str(user.id)}, db)

    assert error.value.status_code == 400
