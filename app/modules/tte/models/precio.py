from sqlalchemy import Boolean, Column, Date, Integer, String
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.tte.models.condicion import Condicion
from app.modules.tte.models.precio_detalle import PrecioDetalle


class Precio(Base):
    __tablename__ = "tte_precio"

    codigo_precio_pk = Column(Integer, primary_key=True, index=True)
    codigo_empresa_fk = Column(Integer, nullable=False)
    nombre = Column(String(80), nullable=True)
    fecha_vence = Column(Date, nullable=True)
    omitir_descuento = Column(Boolean, nullable=True, default=False)
    comentario = Column(String(2000), nullable=True)

    detalles = relationship(PrecioDetalle, backref="precio")
    condiciones = relationship(Condicion, backref="precio")
