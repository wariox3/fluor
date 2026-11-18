from datetime import date, datetime

from pydantic import BaseModel

from app.modules.crm.schemas.solicitud import SolicitudPortalResponse


class SolicitudAnalisisPortalResponse(BaseModel):
    codigo_solicitud_analisis_pk: int
    fecha: date | None = None
    razon: str | None = None
    causa_raiz: str | None = None

    model_config = {"from_attributes": True}


class SolicitudSeguimientoPortalResponse(BaseModel):
    codigo_solicitud_seguimiento_pk: int
    fecha: date | None = None
    plan_accion: str | None = None
    descripcion: str | None = None

    model_config = {"from_attributes": True}


class SolicitudRespuestaPortalResponse(BaseModel):
    codigo_solicitud_respuesta_pk: int
    fecha: datetime | None = None
    respuesta: str | None = None

    model_config = {"from_attributes": True}


class SolicitudPortalDetalleResponse(SolicitudPortalResponse):
    """PQRS del cliente con su tema, el contacto que la registró y su gestión en holmio."""

    tema_nombre: str | None = None
    nombre_contacto: str | None = None
    numero_identificacion_contacto: str | None = None
    telefono_contacto: str | None = None
    correo_contacto: str | None = None
    cargo_contacto: str | None = None
    analisis: list[SolicitudAnalisisPortalResponse] = []
    seguimientos: list[SolicitudSeguimientoPortalResponse] = []
    respuestas: list[SolicitudRespuestaPortalResponse] = []
    # Archivos cargados a la PQRS en `doc_archivo` y marcados para el portal; 0 si no tiene
    cantidad_archivos: int = 0
