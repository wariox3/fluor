from datetime import date, datetime

from pydantic import BaseModel


class VisitaPortalResponse(BaseModel):
    """Visita que la empresa le hizo al cliente."""

    codigo_visita_pk: int
    fecha: datetime | None = None
    codigo_visita_tipo_fk: str | None = None
    visita_tipo_nombre: str | None = None
    codigo_visita_motivo_fk: str | None = None
    visita_motivo_nombre: str | None = None
    codigo_asesor_fk: int | None = None
    asesor_nombre: str | None = None

    model_config = {"from_attributes": True}


class VisitaPortalListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[VisitaPortalResponse]


class VisitaCompromisoResponse(BaseModel):
    """Compromiso acordado en la visita."""

    codigo_visita_compromiso_pk: int
    fecha: date | None = None
    nombre: str | None = None
    detalle: str | None = None
    # Si el compromiso es del cliente (True) o de la empresa (False)
    cliente: bool
    estado_atendido: bool

    model_config = {"from_attributes": True}


class VisitaReporteResponse(BaseModel):
    """Reporte de la persona del cliente que atendió la visita."""

    codigo_visita_reporte_pk: int
    fecha: datetime | None = None
    nombre_contacto: str | None = None
    cargo: str | None = None
    reporte: str | None = None

    model_config = {"from_attributes": True}


class VisitaPortalDetalleResponse(VisitaPortalResponse):
    compromisos: list[VisitaCompromisoResponse]
    reportes: list[VisitaReporteResponse]
    # Archivos cargados a la visita en `doc_archivo`; 0 si no tiene
    cantidad_archivos: int = 0
