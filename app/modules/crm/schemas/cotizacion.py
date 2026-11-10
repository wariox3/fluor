from datetime import date

from pydantic import BaseModel


class CotizacionPortalResponse(BaseModel):
    """Cotización del cliente, con los nombres de su tipo, asesor, forma de pago y negocio."""

    codigo_cotizacion_pk: int
    numero: int | None = None
    fecha: date | None = None
    vencimiento: date | None = None
    codigo_cotizacion_tipo_fk: str | None = None
    cotizacion_tipo_nombre: str | None = None
    codigo_tercero_fk: int | None = None
    tercero_nombre_corto: str | None = None
    codigo_asesor_fk: int | None = None
    asesor_nombre: str | None = None
    codigo_forma_pago_fk: str | None = None
    forma_pago_nombre: str | None = None
    codigo_negocio_fk: int | None = None
    negocio_nombre: str | None = None
    vr_subtotal: float
    vr_iva: float
    vr_neto: float
    vr_total: float
    estado_autorizado: bool | None = None
    estado_aprobado: bool | None = None
    estado_anulado: bool | None = None

    model_config = {"from_attributes": True}


class CotizacionPortalListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[CotizacionPortalResponse]
