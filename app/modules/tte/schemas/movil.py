from datetime import datetime
from pydantic import BaseModel, Field


class MovilGuiaResponse(BaseModel):
    codigo_despacho_detalle: int
    codigo_guia: int
    documento_cliente: str | None
    nombre_remitente: str | None
    nombre_destinatario: str | None
    direccion_destinatario: str | None
    telefono_destinatario: str | None
    ciudad_destino: str | None
    unidades: float
    peso_real: float
    vr_recaudo: float
    vr_cobro_entrega: float
    orden_ruta: int | None
    latitud: float | None
    longitud: float | None
    requiere_cita: bool
    comentario: str | None
    estado_entregado: bool
    estado_novedad: bool
    fecha_entrega: datetime | None


class MovilDespachoGuiasResponse(BaseModel):
    tenant_despacho_id: int
    tenant_id: int
    tenant_nombre: str | None
    codigo_despacho: int
    numero: int | None
    fecha_salida: datetime | None
    total: int
    guias: list[MovilGuiaResponse]


class MovilUbicacionRequest(BaseModel):
    latitud: float = Field(ge=-90, le=90)
    longitud: float = Field(ge=-180, le=180)
    velocidad: float | None = None
    altitud: float | None = None
    exactitud: float | None = None
    exactitud_altitud: float | None = None


class MovilUbicacionLoteItem(MovilUbicacionRequest):
    fecha: datetime = Field(description="Momento de captura en el teléfono; con zona horaria o en hora del negocio")


class MovilUbicacionLoteRequest(BaseModel):
    ubicaciones: list[MovilUbicacionLoteItem] = Field(min_length=1, max_length=500)


class MovilUbicacionLoteResponse(BaseModel):
    codigo_despacho: int
    recibidas: int
    registradas: int
    duplicadas: int
    fecha_ultimo_reporte: datetime | None


class MovilUbicacionResponse(BaseModel):
    codigo_ubicacion: int
    codigo_despacho: int
    fecha: datetime
    latitud: float
    longitud: float
