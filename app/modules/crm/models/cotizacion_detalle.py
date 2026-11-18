from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String, Time
from sqlalchemy.orm import relationship

from app.core.tenant_database import Base
from app.modules.gen.models.item import Item
from app.modules.tur.models.modalidad import Modalidad


class CotizacionDetalle(Base):
    """Servicio cotizado (línea de la cotización), como lo liquida holmio.

    Solo se mapean las columnas de la cotización de servicios de vigilancia; las de transporte
    (ciudades, guía, empaque…) quedan con su valor por defecto en la base.
    """

    __tablename__ = "crm_cotizacion_detalle"

    codigo_cotizacion_detalle_pk = Column(Integer, primary_key=True, index=True)
    codigo_cotizacion_fk = Column(Integer, ForeignKey("crm_cotizacion.codigo_cotizacion_pk"), nullable=True, index=True)
    codigo_modalidad_fk = Column(String(10), ForeignKey("tur_modalidad.codigo_modalidad_pk"), nullable=True, index=True)
    codigo_item_fk = Column(Integer, ForeignKey("gen_item.codigo_item_pk"), nullable=False, index=True)
    codigo_impuesto_iva_fk = Column(String(5), nullable=True)

    cantidad = Column(Integer, nullable=False, default=0)
    # M = mensual (30 días con semanas de 4 días), D = por días entre fecha desde y hasta
    periodo = Column(String(1), nullable=True)
    anio = Column(Integer, nullable=False, default=0)
    mes = Column(Integer, nullable=False, default=0)
    dia_desde = Column(Integer, nullable=False, default=0)
    dia_hasta = Column(Integer, nullable=False, default=0)
    fecha_desde = Column(Date, nullable=True)
    fecha_hasta = Column(Date, nullable=True)
    hora_desde = Column(Time, nullable=True)
    hora_hasta = Column(Time, nullable=True)
    horario = Column(String(300), nullable=True)
    detalle = Column(String(300), nullable=True)
    comentarios = Column(String(500), nullable=True)

    # Días de la semana en que se presta el servicio
    lunes = Column(Boolean, nullable=False, default=False)
    martes = Column(Boolean, nullable=False, default=False)
    miercoles = Column(Boolean, nullable=False, default=False)
    jueves = Column(Boolean, nullable=False, default=False)
    viernes = Column(Boolean, nullable=False, default=False)
    sabado = Column(Boolean, nullable=False, default=False)
    domingo = Column(Boolean, nullable=False, default=False)
    festivo = Column(Boolean, nullable=False, default=False)

    # Horas del servicio: por día (unidad) y liquidadas en el periodo
    horas = Column(Float, nullable=False, default=0.0)
    horas_diurnas = Column(Float, nullable=False, default=0.0)
    horas_nocturnas = Column(Float, nullable=False, default=0.0)
    horas_unidad = Column(Float, nullable=True)
    horas_diurnas_unidad = Column(Float, nullable=True)
    horas_nocturnas_unidad = Column(Float, nullable=True)

    # Valores
    vr_salario_base = Column(Float, nullable=False, default=0.0)
    vr_precio = Column(Float, nullable=True)
    vr_precio_minimo = Column(Float, nullable=True)
    vr_precio_ajustado = Column(Float, nullable=True)
    vr_precio_adicional = Column(Float, nullable=False, default=0.0)
    porcentaje_descuento = Column(Float, nullable=True)
    vr_descuento = Column(Float, nullable=True)
    vr_subtotal = Column(Float, nullable=True)
    vr_subtotal_bruto = Column(Float, nullable=False, default=0.0)
    porcentaje_iva = Column(Integer, nullable=True)
    porcentaje_base_iva = Column(Float, nullable=True)
    vr_base_iva = Column(Float, nullable=False, default=0.0)
    vr_base_aiu = Column(Float, nullable=False, default=0.0)
    vr_iva = Column(Float, nullable=True)
    vr_neto = Column(Float, nullable=False, default=0.0)
    vr_total = Column(Float, nullable=True)
    vr_total_detalle = Column(Float, nullable=False, default=0.0)
    vr_total_detalle_afectado = Column(Float, nullable=False, default=0.0)
    vr_total_detalle_pendiente = Column(Float, nullable=False, default=0.0)
    vr_total_detalle_devolucion = Column(Float, nullable=False, default=0.0)
    vr_total_detalle_adicion = Column(Float, nullable=False, default=0.0)

    # Estados
    compuesto = Column(Boolean, nullable=False, default=False)
    cortesia = Column(Boolean, nullable=False, default=False)
    programar = Column(Boolean, nullable=False, default=False)
    estado_terminado = Column(Boolean, nullable=False, default=False)

    # Relaciones
    modalidad_rel = relationship(Modalidad, foreign_keys=[codigo_modalidad_fk])
    item_rel = relationship(Item, foreign_keys=[codigo_item_fk])

    @property
    def modalidad_nombre(self) -> str | None:
        return self.modalidad_rel.nombre if self.modalidad_rel else None

    @property
    def item_nombre(self) -> str | None:
        return self.item_rel.nombre if self.item_rel else None
