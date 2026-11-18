from datetime import date, time
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


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


class CotizacionPortalDetalleResponse(CotizacionPortalResponse):
    """Encabezado de la cotización para su detalle en el portal."""

    codigo_sector_fk: str | None = None
    estrato: int | None = None
    tiempo_entrega: str | None = None
    comentarios: str | None = None
    vr_descuento: float
    costo_envio: float | None = None


class CotizacionTipoPortalResponse(BaseModel):
    """Tipo de cotización que el cliente puede solicitar desde el portal."""

    codigo_cotizacion_tipo_pk: str
    nombre: str

    model_config = {"from_attributes": True}


class CotizacionPortalNuevoRequest(BaseModel):
    """Cotización nueva del cliente; el tercero es el cliente de su membresía."""

    model_config = {"extra": "forbid"}

    codigo_cotizacion_tipo_fk: str = Field(min_length=1, max_length=10)
    # Como terbio: comercial o residencial
    codigo_sector_fk: Literal["COM", "RES"]
    estrato: int | None = Field(default=None, ge=1, le=6)
    comentarios: str | None = Field(default=None, max_length=500)

    @field_validator("comentarios")
    @classmethod
    def _vacio_a_none(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        return v or None


class CotizacionDetallePortalResponse(BaseModel):
    """Servicio cotizado, con las horas y valores que liquidó fluor."""

    codigo_cotizacion_detalle_pk: int
    codigo_item_fk: int
    item_nombre: str | None = None
    codigo_modalidad_fk: str | None = None
    modalidad_nombre: str | None = None
    cantidad: int
    fecha_desde: date | None = None
    fecha_hasta: date | None = None
    hora_desde: time | None = None
    hora_hasta: time | None = None
    horario: str | None = None
    lunes: bool
    martes: bool
    miercoles: bool
    jueves: bool
    viernes: bool
    sabado: bool
    domingo: bool
    festivo: bool
    horas: float
    horas_diurnas: float
    horas_nocturnas: float
    vr_precio_minimo: float | None = None
    vr_subtotal: float | None = None
    vr_iva: float | None = None
    vr_total_detalle: float

    model_config = {"from_attributes": True}


class CotizacionDetallePortalNuevoRequest(BaseModel):
    """Servicio que el cliente agrega a su cotización (periodo mensual, como terbio)."""

    model_config = {"extra": "forbid"}

    # Como terbio: SAR sin arma, CAR con arma, CAN canino
    codigo_modalidad_fk: Literal["SAR", "CAR", "CAN"]
    cantidad: int = Field(ge=1, le=1000)
    fecha_desde: date
    fecha_hasta: date
    # 00:00 a 00:00 es un servicio de 24 horas
    hora_desde: time
    hora_hasta: time
    lunes: bool = True
    martes: bool = True
    miercoles: bool = True
    jueves: bool = True
    viernes: bool = True
    sabado: bool = True
    domingo: bool = True
    festivo: bool = True

    @model_validator(mode="after")
    def _validar(self):
        if self.fecha_hasta < self.fecha_desde:
            raise ValueError("La fecha hasta no puede ser anterior a la fecha desde")
        if not any((self.lunes, self.martes, self.miercoles, self.jueves,
                    self.viernes, self.sabado, self.domingo, self.festivo)):
            raise ValueError("Selecciona al menos un día del servicio")
        return self


class CotizacionDetallePortalEliminarRequest(BaseModel):
    """Servicios de la cotización que el cliente quiere quitar."""

    model_config = {"extra": "forbid"}

    ids: list[int] = Field(min_length=1, max_length=200)
