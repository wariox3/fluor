from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime, Numeric, Float
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.gen.models.tercero import Tercero
from app.modules.tte.models.guia_tipo import GuiaTipo
from app.modules.tte.models.operacion import Operacion

class Guia(Base):
    __tablename__ = "tte_guia"

    codigo_guia_pk = Column(Integer, primary_key=True, index=True)     
    codigo_guia_tipo_fk = Column(String(20), ForeignKey("tte_guia_tipo.codigo_guia_tipo_pk"))
    codigo_operacion_ingreso_fk = Column(String(20), ForeignKey("tte_operacion.codigo_operacion_pk"))
    codigo_operacion_cargo_fk = Column(String(20), ForeignKey("tte_operacion.codigo_operacion_pk"))
    codigo_tercero_fk = Column(Integer, ForeignKey("gen_tercero.codigo_tercero_pk"))
    unidades = Column(Numeric(precision=10, scale=2))
    peso_real = Column(Numeric(precision=10, scale=2))
    peso_volumen = Column(Numeric(precision=10, scale=2))
    vr_declara = Column(Float)
    vr_flete = Column(Float)
    vr_manejo = Column(Float)
    documento_cliente = Column(String)
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

    tercero = relationship(Tercero, backref="guias")
    guia_tipo = relationship(GuiaTipo, backref="guias")
    operacion_ingreso = relationship(
        Operacion,
        foreign_keys=[codigo_operacion_ingreso_fk],
        backref="guias_operacion_ingreso"
    )
    operacion_cargo = relationship(
        Operacion,
        foreign_keys=[codigo_operacion_cargo_fk],
        backref="guias_operacion_cargo"
    )
