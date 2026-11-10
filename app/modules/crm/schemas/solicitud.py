from datetime import date

from pydantic import BaseModel


class SolicitudPortalResponse(BaseModel):
    """PQRS del cliente, con los nombres de su tipo y del canal por el que llegó."""

    codigo_solicitud_pk: int
    descripcion: str | None = None
    codigo_solicitud_tipo_fk: str | None = None
    solicitud_tipo_nombre: str | None = None
    codigo_tercero_fk: int | None = None
    tercero_nombre_corto: str | None = None
    codigo_canal_fk: str | None = None
    canal_nombre: str | None = None
    fecha: date | None = None
    fecha_registro: date | None = None
    fecha_vencimiento: date | None = None
    fecha_respuesta: date | None = None
    fecha_cierre: date | None = None
    estado_autorizado: bool
    estado_aprobado: bool
    estado_anulado: bool
    estado_cerrado: bool

    model_config = {"from_attributes": True}


class SolicitudPortalListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[SolicitudPortalResponse]
