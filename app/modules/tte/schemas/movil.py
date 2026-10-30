from datetime import datetime
from pydantic import BaseModel


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
