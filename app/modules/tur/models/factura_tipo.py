from sqlalchemy import BigInteger, Boolean, Column, Date, Integer, String, Text
from app.core.tenant_database import Base


class FacturaTipo(Base):
    __tablename__ = "tur_factura_tipo"

    codigo_factura_tipo_pk = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    abreviatura = Column(String(10), nullable=False)
    codigo_factura_clase_fk = Column(String(10), nullable=False)
    codigo_empresa_fk = Column(Integer, nullable=False)

    # FKs sin modelo local
    codigo_cuenta_cobrar_tipo_fk = Column(String(20), nullable=True)
    codigo_resolucion_fk = Column(Integer, nullable=True)
    codigo_comprobante_fk = Column(String(20), nullable=True)
    codigo_comprobante_pedido_fk = Column(String(20), nullable=True)
    codigo_interfaz_dian = Column(String(10), nullable=True)
    codigo_documento_cartera = Column(Integer, nullable=True)
    codigo_centro_costo_contabilidad = Column(Integer, nullable=True)
    codigo_cuenta_cliente_fk = Column(String(20), nullable=True)
    codigo_cuenta_cliente_pedido_fk = Column(String(20), nullable=True)
    codigo_cuenta_ingreso_fk = Column(String(20), nullable=True)
    codigo_cuenta_ingreso_gravado_fk = Column(String(20), nullable=True)
    codigo_segmento_fk = Column(String(10), nullable=True)

    operacion = Column(Integer, nullable=False, default=0)
    consecutivo = Column(Integer, nullable=False, default=0)
    prefijo = Column(String(10), nullable=True)
    prefijo_nota_credito = Column(String(10), nullable=True)
    documento_cartera = Column(Integer, nullable=True)
    punto_de_venta_dian = Column(Integer, nullable=True)
    tipo_operacion_dian = Column(String(10), nullable=True)

    # Numeración / vigencia resolución
    fecha_desde_vigencia = Column(Date, nullable=True)
    fecha_hasta_vigencia = Column(Date, nullable=True)
    numeracion_desde = Column(Integer, nullable=True)
    numeracion_hasta = Column(Integer, nullable=True)
    numero_resolucion_dian_factura = Column(BigInteger, nullable=True)

    # Contacto / mensajes
    correo_factura = Column(String(1000), nullable=True)
    direccion_factura = Column(String(1000), nullable=True)
    telefono_factura = Column(String(500), nullable=True)
    mensaje_pago = Column(String(200), nullable=True)
    mensaje_pago_otro_servicio = Column(String(200), nullable=True)

    # Información legal / PDF
    informacion_legal_factura = Column(Text, nullable=True)
    informacion_pago_factura = Column(Text, nullable=True)
    informacion_contacto_factura = Column(Text, nullable=True)
    informacion_resolucion_dian_factura = Column(Text, nullable=True)
    informacion_resolucion_supervigilancia_factura = Column(Text, nullable=True)
    informacion_sucursal_factura = Column(Text, nullable=True)

    # Flags
    genera_cartera = Column(Boolean, nullable=False, default=False)
    nota_credito = Column(Boolean, nullable=True, default=False)
    factura_electronica = Column(Boolean, nullable=False, default=True)
    estado_inactivo = Column(Boolean, nullable=True, default=False)
