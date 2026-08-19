from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.gen.models.asesor import Asesor
from app.modules.gen.models.tercero import Tercero
from app.modules.tte.models.ciudad import Ciudad
from app.modules.tte.models.empaque import Empaque
from app.modules.tte.models.guia_tipo import GuiaTipo
from app.modules.tte.models.operacion import Operacion
from app.modules.tte.models.producto import Producto
from app.modules.tte.models.servicio import Servicio


class Guia(Base):
    __tablename__ = "tte_guia"
    __table_args__ = (
        Index("IDX_FECHA_INGRESO", "fecha_ingreso"),
        Index("IDX_DOCUMENTO_CLIENTE", "documento_cliente"),
    )

    codigo_guia_pk = Column(Integer, primary_key=True, index=True)
    codigo_guia_tipo_fk = Column(String(20), ForeignKey("tte_guia_tipo.codigo_guia_tipo_pk"))
    codigo_operacion_ingreso_fk = Column(String(20), ForeignKey("tte_operacion.codigo_operacion_pk"))
    codigo_operacion_cargo_fk = Column(String(20), ForeignKey("tte_operacion.codigo_operacion_pk"))
    codigo_tercero_fk = Column(Integer, ForeignKey("gen_tercero.codigo_tercero_pk"))
    codigo_adquiriente_fk = Column(Integer, ForeignKey("gen_tercero.codigo_tercero_pk"))
    codigo_asesor_fk = Column(Integer, ForeignKey("gen_asesor.codigo_asesor_pk"), nullable=True)
    codigo_ciudad_origen_fk = Column(String(20), ForeignKey("tte_ciudad.codigo_ciudad_pk"))
    codigo_ciudad_destino_fk = Column(String(20), ForeignKey("tte_ciudad.codigo_ciudad_pk"))
    codigo_empresa_fk = Column(Integer)

    # Documento / cliente
    documento_cliente = Column(String(80), nullable=True)
    documento_cliente_tipo = Column(String(20), nullable=True)
    relacion_cliente = Column(String(100), nullable=True)

    # Remitente
    remitente = Column(String(150), nullable=True)
    codigo_remitente_fk = Column(Integer, nullable=True)
    nombre_remitente = Column(String(150), nullable=True)
    direccion_remitente = Column(String(150), nullable=True)
    telefono_remitente = Column(String(80), nullable=True)

    # Destinatario
    codigo_destinatario_fk = Column(Integer, nullable=True)
    codigo_identificacion_destinatario_fk = Column(String(3), nullable=True)
    numero_identificacion_destinatario = Column(String(20), nullable=True)
    nombre_destinatario = Column(String(150), nullable=True)
    direccion_destinatario = Column(String(150), nullable=True)
    telefono_destinatario = Column(String(80), nullable=True)

    # Fechas
    fecha_ingreso = Column(DateTime, nullable=True)
    fecha_recogido = Column(DateTime, nullable=True)
    fecha_ingreso_operacion = Column(DateTime, nullable=True)
    fecha_despacho = Column(DateTime, nullable=True)
    fecha_entrega = Column(DateTime, nullable=True)
    fecha_cumplido = Column(DateTime, nullable=True)
    fecha_documental = Column(DateTime, nullable=True)
    fecha_soporte = Column(DateTime, nullable=True)
    fecha_factura = Column(DateTime, nullable=True)
    fecha_desembarco = Column(DateTime, nullable=True)
    fecha_interface = Column(DateTime, nullable=True)
    fecha_descargue = Column(DateTime, nullable=True)

    # Pesos y valores
    unidades = Column(Float, nullable=False, default=0.0)
    peso_real = Column(Float, nullable=False, default=0.0)
    peso_volumen = Column(Float, nullable=False, default=0.0)
    peso_facturado = Column(Float, nullable=False, default=0.0)
    vr_declara = Column(Float, nullable=False, default=0.0)
    vr_flete = Column(Float, nullable=False, default=0.0)
    vr_manejo = Column(Float, nullable=False, default=0.0)
    vr_recaudo = Column(Float, nullable=False, default=0.0)
    vr_abono = Column(Float, nullable=False, default=0.0)
    vr_cobro_entrega = Column(Float, nullable=False, default=0.0)
    vr_costo_reexpedicion = Column(Float, nullable=False, default=0.0)
    vr_costo_peso = Column(Float, nullable=False, default=0.0)
    vr_costo_unidades = Column(Float, nullable=False, default=0.0)
    vr_costo_flete = Column(Float, nullable=False, default=0.0)
    cantidad_despachos = Column(Integer, nullable=False, default=0)

    # Estados
    estado_recogido = Column(Boolean, nullable=False, default=False)
    estado_ingreso = Column(Boolean, nullable=False, default=False)
    estado_impreso = Column(Boolean, nullable=False, default=False)
    estado_embarcado = Column(Boolean, nullable=False, default=False)
    estado_despachado = Column(Boolean, nullable=False, default=False)
    estado_redespacho = Column(Boolean, nullable=False, default=False)
    estado_entregado = Column(Boolean, nullable=False, default=False)
    estado_autorizado = Column(Boolean, nullable=True, default=False)
    estado_aprobado = Column(Boolean, nullable=True, default=False)
    estado_soporte = Column(Boolean, nullable=False, default=False)
    estado_cumplido = Column(Boolean, nullable=False, default=False)
    estado_documental = Column(Boolean, nullable=False, default=False)
    estado_recaudo_devolucion = Column(Boolean, nullable=False, default=False)
    estado_recaudo_cobro = Column(Boolean, nullable=False, default=False)
    estado_facturado = Column(Boolean, nullable=False, default=False)
    estado_factura_generada = Column(Boolean, nullable=False, default=False)
    estado_anulado = Column(Boolean, nullable=False, default=False)
    estado_novedad = Column(Boolean, nullable=False, default=False)
    estado_novedad_solucion = Column(Boolean, nullable=False, default=False)
    estado_factura_exportado = Column(Boolean, nullable=False, default=False)
    estado_contabilizado_recaudo = Column(Boolean, nullable=False, default=False)
    estado_contabilizado = Column(Boolean, nullable=False, default=False)
    estado_predigitalizado = Column(Boolean, nullable=False, default=False)
    estado_digitalizado = Column(Boolean, nullable=False, default=False)
    estado_interface = Column(Boolean, nullable=False, default=False)
    estado_interface_soporte = Column(Boolean, nullable=False, default=False)
    estado_salida_cliente = Column(Boolean, nullable=False, default=False)
    estado_anulado_rndc = Column(Boolean, nullable=False, default=False)
    estado_rndc = Column(Boolean, nullable=False, default=False)
    estado_firma = Column(Boolean, nullable=False, default=False)
    estado_cumplir_rndc = Column(Boolean, nullable=False, default=False)
    estado_ruteo = Column(Boolean, nullable=False, default=False)
    estado_decodificado = Column(Boolean, nullable=True, default=None)
    estado_devolucion = Column(Boolean, nullable=False, default=False)

    # FKs a otras entidades (sin modelo local)
    codigo_despacho_fk = Column(Integer, nullable=True)
    codigo_cumplido_fk = Column(Integer, nullable=True)
    codigo_documental_fk = Column(Integer, nullable=True)
    codigo_recaudo_devolucion_fk = Column(Integer, nullable=True)
    codigo_recaudo_cobro_fk = Column(Integer, nullable=True)
    codigo_factura_fk = Column(Integer, nullable=True)
    codigo_factura_planilla_fk = Column(Integer, nullable=True)
    codigo_condicion_fk = Column(Integer, nullable=True)
    codigo_movimiento_fk = Column(Integer, nullable=True)
    codigo_tercero_operacion_fk = Column(Integer, nullable=True)
    codigo_cotizacion_detalle_fk = Column(Integer, nullable=True)
    codigo_liquidacion_fk = Column(Integer, nullable=True)

    # Logística / enrutamiento
    codigo_ruta_fk = Column(String(20), nullable=True)
    codigo_zona_fk = Column(String(20), ForeignKey("tte_zona.codigo_zona_pk"), nullable=True)
    orden_ruta = Column(Integer, nullable=True, default=0)
    franja = Column(String(20), nullable=True)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)

    # FKs de catálogos tte
    codigo_servicio_fk = Column(String(20), ForeignKey("tte_servicio.codigo_servicio_pk"), nullable=True)
    codigo_producto_fk = Column(String(20), ForeignKey("tte_producto.codigo_producto_pk"), nullable=True)
    codigo_empaque_fk = Column(String(20), ForeignKey("tte_empaque.codigo_empaque_pk"), nullable=True)
    codigo_pago_fk = Column(String(3), nullable=True)

    # Flags y campos varios
    factura = Column(Boolean, nullable=False, default=False)
    reexpedicion = Column(Boolean, nullable=False, default=False)
    cortesia = Column(Boolean, nullable=False, default=False)
    mercancia_peligrosa = Column(Boolean, nullable=True, default=False)
    contenido_verificado = Column(Boolean, nullable=True, default=False)
    correccion = Column(Boolean, nullable=False, default=False)
    devolver_documento_cliente = Column(Boolean, nullable=False, default=False)
    requiere_cita = Column(Boolean, nullable=False, default=False)
    destinatario_notificado = Column(Boolean, nullable=True, default=False)

    usuario = Column(String(25), nullable=True)
    usuario_entrega = Column(String(300), nullable=True)
    empaque_referencia = Column(String(80), nullable=True)
    tipo_liquidacion = Column(String(1), nullable=True, default="K")
    numero_factura = Column(Integer, nullable=True)
    importado = Column(String(1), nullable=True)
    comentario = Column(String(2000), nullable=True)
    seguimiento = Column(String(30), nullable=True)
    ui = Column(String(5), nullable=True)
    token = Column(String(50), nullable=True)
    ingreso_rndc = Column(Integer, nullable=True)

    # Relaciones
    tercero = relationship(Tercero, foreign_keys=[codigo_tercero_fk], backref="guias_tercero")
    adquiriente = relationship(Tercero, foreign_keys=[codigo_adquiriente_fk], backref="guias_adquiriente")
    asesor = relationship(Asesor, foreign_keys=[codigo_asesor_fk], backref="guias_asesor")
    guia_tipo = relationship(GuiaTipo, backref="guias_guia_tipo")
    producto = relationship(Producto, backref="guias_producto")
    empaque = relationship(Empaque, backref="guias_empaque")
    servicio = relationship(Servicio, backref="guias_servicio")
    operacion_ingreso = relationship(Operacion, foreign_keys=[codigo_operacion_ingreso_fk], backref="guias_operacion_ingreso")
    operacion_cargo = relationship(Operacion, foreign_keys=[codigo_operacion_cargo_fk], backref="guias_operacion_cargo")
    ciudad_origen = relationship(Ciudad, foreign_keys=[codigo_ciudad_origen_fk], backref="guias_ciudad_origen")
    ciudad_destino = relationship(Ciudad, foreign_keys=[codigo_ciudad_destino_fk], backref="guias_ciudad_destino")
