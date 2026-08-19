from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.tte.models.ciudad import Ciudad
from app.modules.tte.models.condicion_flete import CondicionFlete
from app.modules.tte.models.condicion_manejo import CondicionManejo
from app.modules.tte.models.guia import Guia
from app.modules.tte.models.precio_detalle import PrecioDetalle


class Zona(Base):
    __tablename__ = "tte_zona"

    codigo_zona_pk = Column(String(20), primary_key=True, index=True)
    codigo_empresa_fk = Column(Integer, nullable=False)
    nombre = Column(String(150), nullable=True)

    ciudades = relationship(Ciudad, backref="zona")
    guias = relationship(Guia, backref="zona")
    condiciones_fletes = relationship(CondicionFlete, backref="zona")
    condiciones_manejos = relationship(CondicionManejo, backref="zona")
    precios_detalles = relationship(PrecioDetalle, backref="zona")
