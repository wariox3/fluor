from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.gen.models.sucursal import Sucursal
from app.modules.gen.models.tercero import Tercero
from app.modules.tur.models.factura_tipo import FacturaTipo


class Factura(Base):
    __tablename__ = "tur_factura"

    codigo_factura_pk = Column(Integer, primary_key=True, index=True)

    # FKs sin modelo local
    codigo_factura_tipo_fk = Column(String(10), ForeignKey("tur_factura_tipo.codigo_factura_tipo_pk"), nullable=True)
    codigo_forma_pago_fk = Column(String(10), nullable=True)
    codigo_factura_clase_fk = Column(String(10), nullable=True)
    codigo_factura_criterio_fk = Column(Integer, nullable=True)
    codigo_clase_fk = Column(Integer, nullable=True)
    codigo_factura_motivo_fk = Column(String(10), nullable=True)
    codigo_resolucion_fk = Column(Integer, nullable=True)
    codigo_factura_fk = Column(Integer, ForeignKey("tur_factura.codigo_factura_pk"), nullable=True)
    codigo_cliente_fk = Column(Integer, nullable=True)
    codigo_tercero_fk = Column(Integer, ForeignKey("gen_tercero.codigo_tercero_pk"), nullable=True)
    codigo_sucursal_fk = Column(Integer, ForeignKey("gen_sucursal.codigo_sucursal_pk"), nullable=True)
    codigo_empresa_fk = Column(Integer, nullable=False)

    numero = Column(Integer, nullable=True, default=0)
    prefijo = Column(String(5), nullable=True)
    fecha = Column(Date, nullable=True)
    fecha_vence = Column(Date, nullable=True)
    fecha_validacion = Column(DateTime, nullable=True)
    hora = Column(Time, nullable=True)
    plazo_pago = Column(Integer, nullable=True, default=0)

    soporte = Column(String(300), nullable=True)
    orden_compra = Column(String(200), nullable=True)
    orden_ingreso = Column(String(100), nullable=True)
    remision = Column(String(50), nullable=True)
    comentarios = Column(String(500), nullable=True)
    usuario = Column(String(50), nullable=True)
    descripcion = Column(Text, nullable=True)
    titulo_relacion = Column(Text, nullable=True)
    detalle_relacion = Column(Text, nullable=True)

    # Valores
    vr_iva = Column(Float, nullable=True, default=0.0)
    vr_base_aiu = Column(Float, nullable=True, default=0.0)
    vr_base_iva = Column(Float, nullable=True, default=0.0)
    vr_subtotal = Column(Float, nullable=False, default=0.0)
    vr_subtotal_bruto = Column(Float, nullable=False, default=0.0)
    vr_descuento = Column(Float, nullable=False, default=0.0)
    vr_neto = Column(Float, nullable=False, default=0.0)
    vr_total = Column(Float, nullable=False, default=0.0)
    vr_retencion_fuente = Column(Float, nullable=False, default=0.0)
    vr_retencion_iva = Column(Float, nullable=False, default=0.0)
    vr_autoretencion = Column(Float, nullable=False, default=0.0)
    vr_ica = Column(Float, nullable=False, default=0.0)

    # Estados
    estado_autorizado = Column(Boolean, nullable=False, default=False)
    estado_aprobado = Column(Boolean, nullable=False, default=False)
    estado_anulado = Column(Boolean, nullable=False, default=False)
    estado_contabilizado = Column(Boolean, nullable=False, default=False)

    # Impresión
    imprimir_relacion = Column(Boolean, nullable=False, default=False)
    imprimir_agrupada = Column(Boolean, nullable=False, default=False)
    imprimir_formato = Column(Boolean, nullable=False, default=False)

    # Electrónico
    proceso_factura_electronica = Column(String(2), nullable=True)
    estado_electronico = Column(Boolean, nullable=True, default=False)
    estado_descartado_electronico = Column(Boolean, nullable=True, default=False)
    estado_notificado_electronico = Column(Boolean, nullable=True, default=False)
    estado_descartado_notificado_electronico = Column(Boolean, nullable=True, default=False)
    respuesta_electronico = Column(String(3), nullable=True, default="P")
    respuesta_electronico_fecha = Column(DateTime, nullable=True)
    cue = Column(String(200), nullable=True)
    codigo_externo = Column(String(500), nullable=True)
    cadena_codigo_qr = Column(Text, nullable=True)
    tipo_operacion_dian = Column(String(10), nullable=True)

    # Relaciones
    tercero = relationship(Tercero, foreign_keys=[codigo_tercero_fk], backref="tur_facturas_tercero")
    factura_tipo = relationship(FacturaTipo, foreign_keys=[codigo_factura_tipo_fk], backref="facturas")
    sucursal = relationship(Sucursal, foreign_keys=[codigo_sucursal_fk], backref="tur_facturas_sucursal")
    factura_padre = relationship("Factura", foreign_keys=[codigo_factura_fk], remote_side="Factura.codigo_factura_pk", backref="facturas_hijas")

    @property
    def tercero_nombre_corto(self):
        return self.tercero.nombre_corto if self.tercero else None

    @property
    def factura_tipo_nombre(self):
        return self.factura_tipo.nombre if self.factura_tipo else None
