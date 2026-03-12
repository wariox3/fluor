from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime, Numeric, Float
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.gen.models.tercero import Tercero
from app.modules.tte.models.ciudad import Ciudad
from app.modules.tte.models.empaque import Empaque
from app.modules.tte.models.guia_tipo import GuiaTipo
from app.modules.tte.models.operacion import Operacion
from app.modules.tte.models.producto import Producto
from app.modules.tte.models.servicio import Servicio

class Guia(Base):
    __tablename__ = "tte_guia"

    codigo_guia_pk = Column(Integer, primary_key=True, index=True)     
    codigo_guia_tipo_fk = Column(String(20), ForeignKey("tte_guia_tipo.codigo_guia_tipo_pk"))
    codigo_operacion_ingreso_fk = Column(String(20), ForeignKey("tte_operacion.codigo_operacion_pk"))
    codigo_operacion_cargo_fk = Column(String(20), ForeignKey("tte_operacion.codigo_operacion_pk"))
    codigo_tercero_fk = Column(Integer, ForeignKey("gen_tercero.codigo_tercero_pk"))
    codigo_adquiriente_fk = Column(Integer, ForeignKey("gen_tercero.codigo_tercero_pk"))
    codigo_producto_fk = Column(String(20), ForeignKey("tte_producto.codigo_producto_pk"))
    codigo_empaque_fk = Column(String(20), ForeignKey("tte_empaque.codigo_empaque_pk"))
    codigo_servicio_fk = Column(String(20), ForeignKey("tte_servicio.codigo_servicio_pk"))
    codigo_ciudad_origen_fk = Column(String(20), ForeignKey("tte_ciudad.codigo_ciudad_pk"))
    codigo_ciudad_destino_fk = Column(String(20), ForeignKey("tte_ciudad.codigo_ciudad_pk"))
    codigo_empresa_fk = Column(Integer)
    unidades = Column(Numeric(precision=10, scale=2))
    peso_real = Column(Numeric(precision=10, scale=2))
    peso_volumen = Column(Numeric(precision=10, scale=2))
    vr_declara = Column(Float)
    vr_flete = Column(Float)
    vr_manejo = Column(Float)
    documento_cliente = Column(String)
    remitente = Column(String)
    nombre_destinatario = Column(String)
    direccion_destinatario = Column(String)
    telefono_destinatario = Column(String)
    estado_ingreso = Column(Boolean, default=False)
    fecha_ingreso = Column(DateTime)
    estado_despachado = Column(Boolean, default=False)
    fecha_despacho = Column(DateTime)
    estado_entregado = Column(Boolean, default=False)
    fecha_entrega = Column(DateTime)
    estado_cumplido = Column(Boolean, default=False)
    fecha_cumplido = Column(DateTime)
    estado_novedad = Column(Boolean, default=False)
    estado_novedad_solucion = Column(Boolean, default=False)

    tercero = relationship(Tercero, foreign_keys=[codigo_tercero_fk], backref="guias_tecero")
    adquiriente = relationship(Tercero, foreign_keys=[codigo_adquiriente_fk], backref="guias_adquiriente")
    guia_tipo = relationship(GuiaTipo, backref="guias_guia_tipo")
    producto = relationship(Producto, backref="guias_producto")
    empaque = relationship(Empaque, backref="guias_empaque")
    servicio = relationship(Servicio, backref="guias_servicio")
    operacion_ingreso = relationship(Operacion, foreign_keys=[codigo_operacion_ingreso_fk], backref="guias_operacion_ingreso")
    operacion_cargo = relationship(Operacion, foreign_keys=[codigo_operacion_cargo_fk], backref="guias_operacion_cargo")
    ciudad_origen = relationship(Ciudad, foreign_keys=[codigo_ciudad_origen_fk], backref="guias_ciudad_origen")
    ciudad_destino = relationship(Ciudad, foreign_keys=[codigo_ciudad_destino_fk], backref="guias_ciudad_destino")
