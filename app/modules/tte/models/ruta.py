from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.tte.models.operacion import Operacion


class Ruta(Base):
    __tablename__ = "tte_ruta"

    codigo_ruta_pk = Column(String(20), primary_key=True, index=True)
    nombre = Column(String(100), nullable=True)
    codigo_despacho_clase_fk = Column(String(5), nullable=True)
    codigo_operacion_fk = Column(String(20), ForeignKey("tte_operacion.codigo_operacion_pk"), nullable=True)
    codigo_empresa_fk = Column(Integer, nullable=False)

    operacion = relationship(Operacion, foreign_keys=[codigo_operacion_fk], backref="rutas_operacion")
