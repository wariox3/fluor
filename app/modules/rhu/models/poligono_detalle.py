from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.core.tenant_database import Base
from app.modules.rhu.models.arma import Arma


class PoligonoDetalle(Base):
    """Arma con la que el empleado presentó el polígono."""

    __tablename__ = "rhu_poligono_detalle"

    codigo_poligono_detalle_pk = Column(Integer, primary_key=True, index=True)
    codigo_poligono_fk = Column(Integer, ForeignKey("rhu_poligono.codigo_poligono_pk"), nullable=True, index=True)
    codigo_arma_fk = Column(Integer, ForeignKey("rhu_arma.codigo_arma_pk"), nullable=True, index=True)

    arma_rel = relationship(Arma, foreign_keys=[codigo_arma_fk])
