from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.gen.models.tercero import Tercero
from app.modules.tte.models.condicion import Condicion


class ClienteCondicion(Base):
    __tablename__ = "tte_cliente_condicion"

    codigo_cliente_condicion_pk = Column(Integer, primary_key=True, index=True)
    codigo_tercero_fk = Column(Integer, ForeignKey("gen_tercero.codigo_tercero_pk"), nullable=True)
    codigo_condicion_fk = Column(Integer, ForeignKey("tte_condicion.codigo_condicion_pk"), nullable=True)
    codigo_cliente_fk = Column(Integer, nullable=True)

    tercero = relationship(Tercero, foreign_keys=[codigo_tercero_fk], backref="clientes_condiciones_tercero_rel")
    condicion = relationship(Condicion, foreign_keys=[codigo_condicion_fk], backref="clientes_condiciones_condicion_rel")

    @hybrid_property
    def tercero_nombre(self):
        return self.tercero.nombre_corto if self.tercero else None

    @hybrid_property
    def condicion_nombre(self):
        return self.condicion.nombre if self.condicion else None
