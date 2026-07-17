from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.tte.models.guia import Guia
from app.modules.tte.models.operacion import Operacion
from app.modules.tte.models.seguimiento_tipo import SeguimientoTipo


class Seguimiento(Base):
    __tablename__ = "tte_seguimiento"

    codigo_seguimiento_pk = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo_guia_fk = Column(Integer, ForeignKey("tte_guia.codigo_guia_pk"), nullable=True)
    codigo_seguimiento_tipo_fk = Column(String(30), ForeignKey("tte_seguimiento_tipo.codigo_seguimiento_tipo_pk"), nullable=True)
    fecha = Column(DateTime, nullable=True)
    fecha_seguimiento = Column(DateTime, nullable=True)
    usuario = Column(String(50), nullable=True)
    codigo_operacion_fk = Column(String(20), ForeignKey("tte_operacion.codigo_operacion_pk"), nullable=True)
    comentario = Column(String(300), nullable=True)
    estado_interface = Column(Boolean, nullable=False, default=False)
    estado_descartado = Column(Boolean, nullable=False, default=False)
    datos = Column(Text, nullable=True)
    latitud = Column(Float, nullable=True, default=0.0)
    longitud = Column(Float, nullable=True, default=0.0)

    # Relaciones
    guia = relationship(Guia, backref="seguimientos_guia")
    seguimiento_tipo = relationship(SeguimientoTipo, backref="seguimientos_seguimiento_tipo")
    operacion = relationship(Operacion, backref="seguimientos_operacion")
