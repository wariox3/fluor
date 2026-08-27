from sqlalchemy import Boolean, Column, DateTime, Date, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.gen.models.tercero import Tercero
from app.modules.tte.models.ciudad import Ciudad
from app.modules.tte.models.conductor import Conductor
from app.modules.tte.models.operacion import Operacion
from app.modules.tte.models.ruta import Ruta


class Despacho(Base):
    __tablename__ = "tte_despacho"
    __table_args__ = (
        Index("IDX_FECHA_SALIDA", "fecha_salida"),
    )

    codigo_despacho_pk = Column(Integer, primary_key=True, index=True)
    numero = Column(Integer, nullable=True, default=0)
    numero_rndc = Column(String(40), nullable=True)

    # Fechas
    fecha = Column(Date, nullable=True)
    fecha_registro = Column(DateTime, nullable=True)
    fecha_salida = Column(DateTime, nullable=True)
    fecha_llegada = Column(DateTime, nullable=True)
    fecha_soporte = Column(DateTime, nullable=True)
    fecha_entrega = Column(DateTime, nullable=True)
    fecha_ultimo_reporte = Column(DateTime, nullable=True)
    fecha_liquidacion = Column(DateTime, nullable=True)

    # FKs con modelo local
    codigo_operacion_fk = Column(String(20), ForeignKey("tte_operacion.codigo_operacion_pk"), nullable=True)
    codigo_ciudad_origen_fk = Column(String(20), ForeignKey("tte_ciudad.codigo_ciudad_pk"), nullable=True)
    codigo_ciudad_destino_fk = Column(String(20), ForeignKey("tte_ciudad.codigo_ciudad_pk"), nullable=True)
    codigo_ruta_fk = Column(String(20), ForeignKey("tte_ruta.codigo_ruta_pk"), nullable=True)
    codigo_cliente_fk = Column(Integer, ForeignKey("gen_tercero.codigo_tercero_pk"), nullable=True)
    codigo_tercero_fk = Column(Integer, ForeignKey("gen_tercero.codigo_tercero_pk"), nullable=True)
    codigo_tercero_anticipo_fk = Column(Integer, ForeignKey("gen_tercero.codigo_tercero_pk"), nullable=True)
    codigo_conductor_fk = Column(Integer, ForeignKey("tte_conductor.codigo_conductor_pk"), nullable=True)

    # FKs a otras entidades (sin modelo local)
    codigo_responsable_cargue_fk = Column(String(1), nullable=True)
    codigo_responsable_descargue_fk = Column(String(1), nullable=True)
    codigo_vehiculo_fk = Column(String(20), nullable=True)
    codigo_vehiculo_remolque_fk = Column(String(20), nullable=True)
    codigo_poseedor_fk = Column(Integer, nullable=True)
    codigo_despacho_clase_fk = Column(String(5), nullable=True)
    codigo_despacho_tipo_fk = Column(String(20), nullable=True)
    codigo_anticipo_tipo_fk = Column(Integer, nullable=True)
    codigo_usuario_externo_fk = Column(Integer, nullable=True)
    codigo_cotizacion_detalle_fk = Column(Integer, nullable=True)
    codigo_empresa_fk = Column(Integer, nullable=False)

    # Cantidades y pesos
    cantidad = Column(Integer, nullable=False, default=0)
    cantidad_entregada = Column(Integer, nullable=False, default=0)
    unidades = Column(Float, nullable=False, default=0.0)
    peso_real = Column(Float, nullable=False, default=0.0)
    peso_real_original = Column(Float, nullable=False, default=0.0)
    peso_volumen = Column(Float, nullable=False, default=0.0)
    peso_costo = Column(Float, nullable=False, default=0.0)

    # Valores
    vr_declara = Column(Float, nullable=False, default=0.0)
    vr_flete = Column(Float, nullable=False, default=0.0)
    vr_manejo = Column(Float, nullable=False, default=0.0)
    vr_otros = Column(Float, nullable=False, default=0.0)
    vr_recaudo = Column(Float, nullable=False, default=0.0)
    vr_contra_entrega = Column(Float, nullable=False, default=0.0)
    vr_flete_pago = Column(Float, nullable=False, default=0.0)
    vr_otros_conceptos = Column(Float, nullable=False, default=0.0)
    vr_flete_regulado = Column(Float, nullable=False, default=0.0)
    vr_anticipo = Column(Float, nullable=False, default=0.0)
    vr_anticipo_otros = Column(Float, nullable=False, default=0.0)
    vr_anticipo_tercero = Column(Float, nullable=False, default=0.0)
    vr_industria_comercio = Column(Float, nullable=False, default=0.0)
    vr_retencion_fuente = Column(Float, nullable=False, default=0.0)
    vr_retencion_fopat = Column(Float, nullable=False, default=0.0)
    vr_total = Column(Float, nullable=False, default=0.0)
    vr_total_neto = Column(Float, nullable=False, default=0.0)
    vr_descuento_papeleria = Column(Float, nullable=False, default=0.0)
    vr_descuento_seguridad = Column(Float, nullable=False, default=0.0)
    vr_descuento_cargue = Column(Float, nullable=False, default=0.0)
    vr_descuento_estampilla = Column(Float, nullable=False, default=0.0)
    vr_cobro_entrega = Column(Float, nullable=False, default=0.0)
    vr_cobro_entrega_rechazado = Column(Float, nullable=False, default=0.0)
    vr_saldo = Column(Float, nullable=False, default=0.0)
    vr_costo = Column(Float, nullable=True, default=0.0)
    vr_costo_pago = Column(Float, nullable=False, default=0.0)
    vr_intermediacion = Column(Float, nullable=False, default=0.0)
    vr_intermediacion_final = Column(Float, nullable=False, default=0.0)

    # Valores originales (antes de correcciones)
    vr_flete_pago_original = Column(Float, nullable=False, default=0.0)
    vr_anticipo_original = Column(Float, nullable=False, default=0.0)
    vr_industria_comercio_original = Column(Float, nullable=False, default=0.0)
    vr_retencion_fuente_original = Column(Float, nullable=False, default=0.0)
    vr_total_original = Column(Float, nullable=False, default=0.0)
    vr_total_neto_original = Column(Float, nullable=False, default=0.0)

    # Porcentajes
    porcentaje_rentabilidad = Column(Float, nullable=True, default=0.0)
    porcentaje = Column(Float, nullable=False, default=0.0)
    porcentaje_final = Column(Float, nullable=False, default=0.0)

    # Estados
    estado_monitoreo = Column(Boolean, nullable=True, default=False)
    estado_autorizado = Column(Boolean, nullable=True, default=False)
    estado_aprobado = Column(Boolean, nullable=True, default=False)
    estado_cerrado = Column(Boolean, nullable=True, default=False)
    estado_entregado = Column(Boolean, nullable=False, default=False)
    estado_soporte = Column(Boolean, nullable=True, default=False)
    estado_anulado = Column(Boolean, nullable=True, default=False)
    estado_contabilizado = Column(Boolean, nullable=True, default=False)
    estado_cumplir_rndc = Column(Boolean, nullable=True, default=False)
    estado_novedad = Column(Boolean, nullable=True, default=False)
    estado_novedad_solucion = Column(Boolean, nullable=True, default=False)
    estado_egreso = Column(Boolean, nullable=True, default=False)
    estado_rndc = Column(Boolean, nullable=True, default=False)
    estado_anulado_rndc = Column(Boolean, nullable=True, default=False)
    estado_descartado_rndc = Column(Boolean, nullable=False, default=False)
    estado_interface = Column(Boolean, nullable=True, default=False)
    estado_liquidado = Column(Boolean, nullable=False, default=False)
    estado_intermediacion = Column(Boolean, nullable=False, default=False)

    # Flags y campos varios
    propio = Column(Boolean, nullable=True, default=False)
    cuenta_pagar = Column(Boolean, nullable=True, default=False)
    destinatario_notificado = Column(Boolean, nullable=True, default=False)
    tipo_despacho_operacion_rndc = Column(String(1), nullable=True, default="G")
    precinto = Column(String(30), nullable=True)
    comentario = Column(String(2000), nullable=True)
    correccion_entrega_comentario = Column(Text, nullable=True)
    usuario = Column(String(25), nullable=True)
    usuario_liquidacion = Column(String(25), nullable=True)
    api_token = Column(String(20), nullable=True)
    ultima_latitud = Column(Float, nullable=True, default=0.0)
    ultima_longitud = Column(Float, nullable=True, default=0.0)

    # Relaciones
    operacion = relationship(Operacion, foreign_keys=[codigo_operacion_fk], backref="despachos_operacion")
    ciudad_origen = relationship(Ciudad, foreign_keys=[codigo_ciudad_origen_fk], backref="despachos_ciudad_origen")
    ciudad_destino = relationship(Ciudad, foreign_keys=[codigo_ciudad_destino_fk], backref="despachos_ciudad_destino")
    ruta = relationship(Ruta, foreign_keys=[codigo_ruta_fk], backref="despachos_ruta")
    cliente = relationship(Tercero, foreign_keys=[codigo_cliente_fk], backref="despachos_cliente")
    tercero = relationship(Tercero, foreign_keys=[codigo_tercero_fk], backref="despachos_tercero")
    tercero_anticipo = relationship(Tercero, foreign_keys=[codigo_tercero_anticipo_fk], backref="despachos_tercero_anticipo")
    conductor = relationship(Conductor, foreign_keys=[codigo_conductor_fk], backref="despachos_conductor")
