from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.gen.models.tercero import Tercero


class TerceroOperacion(Base):
    __tablename__ = "tte_tercero_operacion"

    codigo_tercero_operacion_pk = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo_tercero_fk = Column(Integer, ForeignKey("gen_tercero.codigo_tercero_pk"), nullable=False)
    codigo = Column(String(20), nullable=True)
    nombre = Column(String(150), nullable=True)

    tercero = relationship(Tercero, foreign_keys=[codigo_tercero_fk], backref="terceros_operaciones_tercero_rel")

    @hybrid_property
    def tercero_nombre(self):
        return self.tercero.nombre_corto if self.tercero else None
