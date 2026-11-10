from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.tenant_database import Base
from app.modules.crm.models.cotizacion_tipo import CotizacionTipo
from app.modules.crm.models.negocio import Negocio
from app.modules.gen.models.asesor import Asesor
from app.modules.gen.models.forma_pago import FormaPago
from app.modules.gen.models.tercero import Tercero


class Cotizacion(Base):
    __tablename__ = "crm_cotizacion"

    codigo_cotizacion_pk = Column(Integer, primary_key=True, index=True)
    codigo_cotizacion_tipo_fk = Column(String(10), ForeignKey("crm_cotizacion_tipo.codigo_cotizacion_tipo_pk"), nullable=True, index=True)
    codigo_tercero_fk = Column(Integer, ForeignKey("gen_tercero.codigo_tercero_pk"), nullable=True, index=True)
    codigo_asesor_fk = Column(Integer, ForeignKey("gen_asesor.codigo_asesor_pk"), nullable=True, index=True)
    codigo_forma_pago_fk = Column(String(10), ForeignKey("gen_forma_pago.codigo_forma_pago_pk"), nullable=True, index=True)
    codigo_negocio_fk = Column(Integer, ForeignKey("crm_negocio.codigo_negocio_pk"), nullable=True, index=True)

    # FKs sin modelo local
    codigo_prospecto_fk = Column(Integer, nullable=True)
    codigo_cotizacion_rechazo_fk = Column(Integer, nullable=True)
    codigo_contacto_fk = Column(Integer, nullable=True)
    codigo_sector_fk = Column(String(10), nullable=True)
    codigo_tercero_respaldo_fk = Column(Integer, nullable=True)
    codigo_sucursal_fk = Column(Integer, nullable=True)

    numero = Column(Integer, nullable=True)
    fecha = Column(Date, nullable=False)
    vencimiento = Column(Date, nullable=True)
    fecha_vence = Column(Date, nullable=True)
    fecha_aceptado = Column(Date, nullable=True)
    fecha_rechazado = Column(Date, nullable=True)
    tiempo_entrega = Column(String(255), nullable=True)
    soporte = Column(String(255), nullable=True)
    plazo_pago = Column(Integer, nullable=False, default=0)
    estrato = Column(Integer, nullable=True)
    contacto = Column(String(200), nullable=True)
    operacion = Column(String(200), nullable=True)
    proyecto = Column(String(200), nullable=True)
    condicion_comercial = Column(String(500), nullable=True)
    comentarios = Column(String(500), nullable=True)
    comentario_rechazado = Column(String(500), nullable=True)
    usuario = Column(String(50), nullable=True)
    mostrar_valor_total_impresion = Column(Boolean, nullable=True, default=True)

    # Horas del servicio cotizado
    horas = Column(Integer, nullable=False, default=0)
    horas_diurnas = Column(Integer, nullable=False, default=0)
    horas_nocturnas = Column(Integer, nullable=False, default=0)

    # Valores
    vr_subtotal = Column(Float, nullable=False, default=0.0)
    vr_subtotal_bruto = Column(Float, nullable=True, default=0.0)
    vr_descuento = Column(Float, nullable=False, default=0.0)
    vr_base_iva = Column(Float, nullable=True, default=0.0)
    vr_iva = Column(Float, nullable=False, default=0.0)
    vr_neto = Column(Float, nullable=False, default=0.0)
    vr_total = Column(Float, nullable=False, default=0.0)
    costo_envio = Column(Float, nullable=True)
    vr_total_precio_ajustado = Column(Float, nullable=False, default=0.0)
    vr_total_precio_minimo = Column(Float, nullable=False, default=0.0)
    vr_total_servicio = Column(Float, nullable=False, default=0.0)
    vr_base_aiu = Column(Float, nullable=False, default=0.0)
    vr_total_costo = Column(Float, nullable=False, default=0.0)
    vr_salario_base = Column(Float, nullable=False, default=0.0)

    # Estados
    estado_autorizado = Column(Boolean, nullable=True, default=False)
    estado_aprobado = Column(Boolean, nullable=True, default=False)
    estado_anulado = Column(Boolean, nullable=True, default=False)
    estado_aceptado = Column(Boolean, nullable=True, default=False)
    estado_rechazado = Column(Boolean, nullable=True, default=False)
    estado_contabilizado = Column(Boolean, nullable=False, default=False)

    # Relaciones
    cotizacion_tipo_rel = relationship(CotizacionTipo, foreign_keys=[codigo_cotizacion_tipo_fk])
    tercero_rel = relationship(Tercero, foreign_keys=[codigo_tercero_fk])
    asesor_rel = relationship(Asesor, foreign_keys=[codigo_asesor_fk])
    forma_pago_rel = relationship(FormaPago, foreign_keys=[codigo_forma_pago_fk])
    negocio_rel = relationship(Negocio, foreign_keys=[codigo_negocio_fk])

    @property
    def cotizacion_tipo_nombre(self) -> str | None:
        return self.cotizacion_tipo_rel.nombre if self.cotizacion_tipo_rel else None

    @property
    def tercero_nombre_corto(self) -> str | None:
        return self.tercero_rel.nombre_corto if self.tercero_rel else None

    @property
    def asesor_nombre(self) -> str | None:
        return self.asesor_rel.nombre if self.asesor_rel else None

    @property
    def forma_pago_nombre(self) -> str | None:
        return self.forma_pago_rel.nombre if self.forma_pago_rel else None

    @property
    def negocio_nombre(self) -> str | None:
        return self.negocio_rel.nombre if self.negocio_rel else None
