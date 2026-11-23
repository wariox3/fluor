"""Auditoría automática de cambios en gen_log_accion.

Un modelo se audita declarando el código de gen_modelo y marcando las columnas a seguir:

    class Guia(Base):
        __tablename__ = "tte_guia"
        __auditoria__ = {"modelo": "TteGuia"}

        vr_flete = Column(Float, info={"auditar": True})

Al crear, editar o eliminar un registro por la sesión (no con query().update()/delete()
ni SQL directo) se inserta una fila en gen_log_accion en la misma transacción.
El usuario se toma de session.info["usuario"] (ver asignar_usuario).
"""
import enum
from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import Integer, event, insert, inspect
from sqlalchemy.orm import Mapper, Session, object_session

from app.core.utils import ahora_local

USUARIO_SISTEMA = "sistema"
ACCION_CREAR = "crear"
ACCION_EDITAR = "editar"
ACCION_ELIMINAR = "eliminar"

# mapper -> (codigo_modelo, [(clave_atributo, nombre_columna)], clave_pk)
_auditados: dict[Mapper, tuple[str, list[tuple[str, str]], str]] = {}


class AuditoriaConfigError(Exception):
    """Un modelo declara __auditoria__ de forma inválida."""


def asignar_usuario(db: Session, current_user: dict | None) -> None:
    """Guarda en la sesión quién hace los cambios: el correo, o el prefijo si es API key."""
    usuario = (current_user or {}).get("email") or (current_user or {}).get("sub")
    db.info["usuario"] = str(usuario)[:200] if usuario else USUARIO_SISTEMA


def activar(base) -> None:
    """Registra los eventos sobre todos los modelos de la base declarativa (tenant)."""
    event.listen(base, "mapper_configured", _configurar, propagate=True)
    event.listen(base, "after_insert", _despues_insertar, propagate=True)
    event.listen(base, "after_update", _despues_actualizar, propagate=True)
    event.listen(base, "before_delete", _antes_eliminar, propagate=True)


def _configurar(mapper: Mapper, clase) -> None:
    config = clase.__dict__.get("__auditoria__")
    if config is None:
        return

    nombre = clase.__name__
    codigo_modelo = config.get("modelo") if isinstance(config, dict) else None
    if not codigo_modelo or not isinstance(codigo_modelo, str):
        raise AuditoriaConfigError(f"{nombre}.__auditoria__ debe indicar 'modelo' (código de gen_modelo)")

    pk = mapper.primary_key
    if len(pk) != 1 or not isinstance(pk[0].type, Integer):
        raise AuditoriaConfigError(
            f"{nombre} no se puede auditar: gen_log_accion.codigo_registro requiere una llave primaria entera simple"
        )

    campos = [
        (prop.key, prop.columns[0].name)
        for prop in mapper.column_attrs
        if prop.columns[0].info.get("auditar")
    ]
    if not campos:
        raise AuditoriaConfigError(f"{nombre}.__auditoria__ no tiene columnas con info={{'auditar': True}}")

    # active_history: carga el valor anterior aunque el atributo no estuviera cargado al asignarlo
    for clave, _ in campos:
        event.listen(getattr(clase, clave), "set", _sin_accion, active_history=True)

    _auditados[mapper] = (codigo_modelo, campos, mapper.get_property_by_column(pk[0]).key)


def _sin_accion(target, value, oldvalue, initiator):
    return value


def _valor(v):
    """Convierte un valor a algo serializable en JSON."""
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (datetime, date, time)):
        return v.isoformat()
    if isinstance(v, enum.Enum):
        return v.value
    if isinstance(v, (bytes, bytearray)):
        return None
    return v


def _registrar(mapper: Mapper, connection, target, accion: str, campos: dict | None) -> None:
    from app.modules.gen.models.log_accion import LogAccion

    codigo_modelo, _, clave_pk = _auditados[mapper]
    sesion = object_session(target)
    usuario = sesion.info.get("usuario", USUARIO_SISTEMA) if sesion else USUARIO_SISTEMA
    connection.execute(
        insert(LogAccion.__table__).values(
            fecha=ahora_local(),
            codigo_modelo_fk=codigo_modelo,
            codigo_registro=getattr(target, clave_pk),
            accion=accion,
            usuario=usuario,
            campos=campos or None,
        )
    )


def _despues_insertar(mapper: Mapper, connection, target) -> None:
    if mapper not in _auditados:
        return
    _, columnas, _ = _auditados[mapper]
    campos = {}
    for clave, nombre in columnas:
        nuevo = _valor(getattr(target, clave))
        if nuevo is not None:
            campos[nombre] = {"anterior": None, "nuevo": nuevo}
    _registrar(mapper, connection, target, ACCION_CREAR, campos)


def _despues_actualizar(mapper: Mapper, connection, target) -> None:
    if mapper not in _auditados:
        return
    _, columnas, _ = _auditados[mapper]
    estado = inspect(target)
    campos = {}
    for clave, nombre in columnas:
        historial = estado.attrs[clave].history
        if not historial.has_changes():
            continue
        anterior = _valor(historial.deleted[0]) if historial.deleted else None
        nuevo = _valor(historial.added[0]) if historial.added else None
        if anterior != nuevo:
            campos[nombre] = {"anterior": anterior, "nuevo": nuevo}
    # Una edición que no toca campos auditados no deja rastro
    if campos:
        _registrar(mapper, connection, target, ACCION_EDITAR, campos)


def _antes_eliminar(mapper: Mapper, connection, target) -> None:
    if mapper not in _auditados:
        return
    _, columnas, _ = _auditados[mapper]
    campos = {}
    for clave, nombre in columnas:
        anterior = _valor(getattr(target, clave))
        if anterior is not None:
            campos[nombre] = {"anterior": anterior, "nuevo": None}
    _registrar(mapper, connection, target, ACCION_ELIMINAR, campos)
