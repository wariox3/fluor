from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import Column, Date, Integer, Numeric, String, create_engine, event
from sqlalchemy.orm import configure_mappers, declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import auditoria
from app.core.auditoria import AuditoriaConfigError
from app.core.tenant_database import Base
from app.modules.gen.models.log_accion import LogAccion
from app.modules.gen.models.modelo import Modelo


class ProductoPrueba(Base):
    __tablename__ = "prueba_auditoria_producto"
    __auditoria__ = {"modelo": "PruebaProducto"}

    codigo_producto_pk = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), info={"auditar": True})
    precio = Column(Numeric(10, 2), info={"auditar": True})
    vence = Column(Date, info={"auditar": True})
    nota = Column(String(50))  # no se audita


class SinAuditoria(Base):
    __tablename__ = "prueba_auditoria_libre"

    codigo_pk = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50))


@pytest.fixture
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)

    @event.listens_for(engine, "connect")
    def _fk(conn, _):
        conn.execute("PRAGMA foreign_keys=ON")

    tablas = [Modelo.__table__, LogAccion.__table__, ProductoPrueba.__table__, SinAuditoria.__table__]
    Base.metadata.create_all(engine, tables=tablas)
    sesion = sessionmaker(autoflush=False, bind=engine)()
    sesion.add(Modelo(codigo_modelo_pk="PruebaProducto"))
    sesion.commit()
    auditoria.asignar_contexto(sesion, {"sub": "7", "email": "ana@empresa.com"})
    yield sesion
    sesion.close()


def _logs(db):
    return db.query(LogAccion).order_by(LogAccion.codigo_log_accion_pk).all()


def test_crear_guarda_valores_iniciales_solo_de_campos_auditados(db):
    p = ProductoPrueba(nombre="Caja", precio=Decimal("10.50"), vence=date(2026, 12, 1), nota="x")
    db.add(p)
    db.commit()

    [log] = _logs(db)
    assert log.accion == "crear"
    assert log.codigo_modelo_fk == "PruebaProducto"
    assert log.codigo_registro == p.codigo_producto_pk
    assert log.usuario == "ana@empresa.com"
    assert log.campos == {
        "nombre": "Caja",
        "precio": 10.5,
        "vence": "2026-12-01",
    }
    assert log.ruta is None  # sin petición HTTP


def test_editar_registra_solo_cambios_reales(db):
    p = ProductoPrueba(nombre="Caja", precio=Decimal("10"))
    db.add(p)
    db.commit()

    # Tras el commit los atributos quedan expirados: el valor anterior debe cargarse igual
    p.nombre = "Caja grande"
    p.precio = Decimal("10")  # mismo valor
    db.commit()

    log = _logs(db)[-1]
    assert log.accion == "editar"
    assert log.campos == {"nombre": "Caja grande"}


def test_editar_a_nulo_registra_el_nulo(db):
    p = ProductoPrueba(nombre="Caja", precio=Decimal("10"))
    db.add(p)
    db.commit()

    p.precio = None
    db.commit()

    assert _logs(db)[-1].campos == {"precio": None}


def test_editar_campo_no_auditado_no_genera_log(db):
    p = ProductoPrueba(nombre="Caja")
    db.add(p)
    db.commit()

    p.nota = "otra"
    db.commit()

    assert [l.accion for l in _logs(db)] == ["crear"]


def test_eliminar_guarda_valores_anteriores(db):
    p = ProductoPrueba(nombre="Caja", precio=Decimal("3"))
    db.add(p)
    db.commit()
    pk = p.codigo_producto_pk

    db.delete(p)
    db.commit()

    log = _logs(db)[-1]
    assert log.accion == "eliminar"
    assert log.codigo_registro == pk
    assert log.campos == {
        "nombre": "Caja",
        "precio": 3.0,
    }


def test_rollback_descarta_el_log(db):
    db.add(ProductoPrueba(nombre="Caja"))
    db.flush()
    db.rollback()

    assert _logs(db) == []


def test_modelo_sin_auditoria_no_genera_log(db):
    db.add(SinAuditoria(nombre="libre"))
    db.commit()

    assert _logs(db) == []


def _request(path, route_path=None):
    from starlette.requests import Request
    scope = {"type": "http", "method": "PUT", "path": path, "headers": [], "query_string": b""}
    if route_path:
        scope["route"] = type("Ruta", (), {"path": route_path})()
    return Request(scope)


def test_ruta_guarda_el_patron_y_se_corta_a_50(db):
    auditoria.asignar_contexto(db, {"email": "ana@empresa.com"}, _request("/tte/guia/123", "/tte/guia/{codigo_guia_pk}"))
    db.add(ProductoPrueba(nombre="Caja"))
    db.commit()
    assert _logs(db)[-1].ruta == "/tte/guia/{codigo_guia_pk}"

    larga = "/tte/" + "a" * 80
    auditoria.asignar_contexto(db, {"email": "ana@empresa.com"}, _request(larga, larga))
    assert db.info["ruta"] == larga[:50]


def test_usuario_api_key_y_sistema(db):
    auditoria.asignar_contexto(db, {"sub": "erp_abc123", "tenant_id": 1})
    assert db.info["usuario"] == "erp_abc123"
    auditoria.asignar_contexto(db, None)
    assert db.info["usuario"] == "sistema"


def test_configuracion_invalida_falla_al_configurar():
    # Base aparte para no dejar el modelo inválido en el registro de las empresas
    BasePrueba = declarative_base()
    auditoria.activar(BasePrueba)

    class LlaveTexto(BasePrueba):
        __tablename__ = "prueba_auditoria_llave_texto"
        __auditoria__ = {"modelo": "X"}
        codigo_pk = Column(String(10), primary_key=True)
        nombre = Column(String(10), info={"auditar": True})

    try:
        with pytest.raises(AuditoriaConfigError, match="llave primaria entera"):
            configure_mappers()
    finally:
        BasePrueba.registry.dispose()


def test_endpoint_lista_historial_de_un_registro(db, client):
    from app.core.security import get_current_user
    from app.core.tenant_database import get_tenant_db
    from app.main import app

    p = ProductoPrueba(nombre="Caja", precio=Decimal("1"))
    otro = ProductoPrueba(nombre="Otro")
    db.add_all([p, otro])
    db.commit()
    p.precio = Decimal("2")
    db.commit()

    app.dependency_overrides[get_tenant_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: {"sub": "7", "email": "ana@empresa.com"}

    r = client.get("/gen/log-accion/lista", params={
        "codigo_modelo_fk": "PruebaProducto",
        "codigo_registro": p.codigo_producto_pk,
    })

    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["total"] == 2
    # Lo más reciente primero
    assert [i["accion"] for i in cuerpo["items"]] == ["editar", "crear"]
    assert cuerpo["items"][0]["campos"] == {"precio": 2.0}
    assert cuerpo["items"][0]["usuario"] == "ana@empresa.com"


def test_endpoint_lista_requiere_autenticacion(client):
    assert client.get("/gen/log-accion/lista").status_code == 401
