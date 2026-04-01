from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from app.core.tenant_database import Base
from sqlalchemy.orm import relationship
from app.modules.gen.models.impuesto import Impuesto


class Item(Base):
    __tablename__ = "gen_item"

    codigo_item_pk = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(400), nullable=True)
    nombre_tecnico = Column("nombre_tenico", String(400), nullable=True)
    vr_costo_predeterminado = Column(Float, nullable=True, default=0.0)
    vr_costo_promedio = Column(Float, nullable=False, default=0.0)
    vr_precio_predeterminado = Column(Float, nullable=True, default=0.0)
    vr_precio_promedio = Column(Float, nullable=True, default=0.0)
    codigo_ean = Column(String(80), nullable=True)
    codigo_barras = Column(String(150), nullable=True)
    porcentaje_iva = Column(Integer, nullable=True, default=0)
    codigo_linea_fk = Column(String(10), nullable=True)
    codigo_grupo_fk = Column(String(10), nullable=True)
    codigo_turno_item_fk = Column(Integer, nullable=True)
    codigo_subgrupo_fk = Column(String(10), nullable=True)
    codigo_unidad_medida_fk = Column(String(10), nullable=True)
    codigo_marca_fk = Column(String(10), nullable=True)
    codigo_impuesto_retencion_fk = Column(String(5), ForeignKey("gen_impuesto.codigo_impuesto_pk"), nullable=True)
    codigo_impuesto_retencion_compra_fk = Column(String(5), ForeignKey("gen_impuesto.codigo_impuesto_pk"), nullable=True)
    codigo_impuesto_iva_venta_fk = Column(String(5), ForeignKey("gen_impuesto.codigo_impuesto_pk"), nullable=True)
    codigo_impuesto_iva_compra_fk = Column(String(5), ForeignKey("gen_impuesto.codigo_impuesto_pk"), nullable=True)
    codigo_impuesto_industria_comercio_fk = Column(String(5), ForeignKey("gen_impuesto.codigo_impuesto_pk"), nullable=True)
    codigo_medida_fk = Column(String(20), nullable=True)
    modelo = Column(String(50), nullable=True)
    referencia = Column(String(50), nullable=True)
    cantidad_existencia = Column(Integer, nullable=True, default=0)
    cantidad_remisionada = Column(Integer, nullable=True, default=0)
    cantidad_control = Column(Integer, nullable=True, default=0)
    cantidad_reservada = Column(Integer, nullable=True, default=0)
    cantidad_disponible = Column(Integer, nullable=True, default=0)
    cantidad_orden = Column(Integer, nullable=True, default=0)
    cantidad_solicitud_compra = Column(Integer, nullable=True, default=0)
    cantidad_solicitud = Column(Integer, nullable=True, default=0)
    cantidad_pedido = Column(Integer, nullable=True, default=0)
    afecta_inventario = Column(Boolean, nullable=True, default=True)
    retencion_industria_comercio = Column(Boolean, nullable=True, default=False)
    descripcion = Column(String(600), nullable=True)
    stock_minimo = Column(Integer, nullable=True, default=0)
    stock_maximo = Column(Integer, nullable=True, default=0)
    codigo_cuenta_venta_fk = Column(String(20), nullable=True)
    codigo_cuenta_venta_devolucion_fk = Column(String(20), nullable=True)
    codigo_cuenta_compra_fk = Column(String(20), nullable=True)
    codigo_cuenta_compra_devolucion_fk = Column(String(20), nullable=True)
    codigo_cuenta_compra_importacion_fk = Column(String(20), nullable=True)
    codigo_cuenta_costo_fk = Column(String(20), nullable=True)
    codigo_cuenta_inventario_fk = Column(String(20), nullable=True)
    codigo_cuenta_inventario_transito_fk = Column(String(20), nullable=True)
    producto = Column(Boolean, nullable=True, default=False)
    servicio = Column(Boolean, nullable=True, default=False)
    servicio_aiu = Column(Boolean, nullable=False, default=False)
    validar_stock = Column(Boolean, nullable=True, default=False)
    activo_fijo = Column(Boolean, nullable=True, default=False)
    registro_invima = Column(String(80), nullable=True)
    dotacion = Column(Boolean, nullable=True, default=False)
    maneja_serie = Column(Boolean, nullable=True, default=False)
    aplica_turno = Column(Boolean, nullable=True, default=False)
    venta = Column(Boolean, nullable=True, default=False)
    compra = Column(Boolean, nullable=True, default=True)
    talla = Column(String(50), nullable=True)
    codigo_dotacion_elemento_fk = Column(Integer, nullable=True)
    codigo_empresa_fk = Column(Integer, nullable=False)
    estado_inactivo = Column(Boolean, nullable=False, default=False)
    codigo_interface = Column(String(20), nullable=True)

    impuesto_retencion = relationship(
        Impuesto,
        foreign_keys=[codigo_impuesto_retencion_fk],
        backref="items_retencion",
    )
    impuesto_retencion_compra = relationship(
        Impuesto,
        foreign_keys=[codigo_impuesto_retencion_compra_fk],
        backref="items_retencion_compra",
    )
    impuesto_iva_venta = relationship(
        Impuesto,
        foreign_keys=[codigo_impuesto_iva_venta_fk],
        backref="items_iva_venta",
    )
    impuesto_iva_compra = relationship(
        Impuesto,
        foreign_keys=[codigo_impuesto_iva_compra_fk],
        backref="items_iva_compra",
    )
    impuesto_industria_comercio = relationship(
        Impuesto,
        foreign_keys=[codigo_impuesto_industria_comercio_fk],
        backref="items_industria_comercio",
    )
