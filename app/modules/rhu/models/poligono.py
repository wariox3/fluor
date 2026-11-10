from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.tenant_database import Base
from app.modules.rhu.models.poligono_detalle import PoligonoDetalle


class Poligono(Base):
    """Prueba de polígono (manejo de armas) que presentó el empleado."""

    __tablename__ = "rhu_poligono"

    codigo_poligono_pk = Column(Integer, primary_key=True, index=True)
    codigo_empleado_fk = Column(Integer, ForeignKey("rhu_empleado.codigo_empleado_pk"), nullable=True, index=True)
    fecha = Column(Date, nullable=True)
    fecha_realizacion = Column(Date, nullable=True)
    fecha_vence = Column(Date, nullable=True)
    numero_registro = Column(String(20), nullable=True)
    comentarios = Column(String(200), nullable=True)
    usuario = Column(String(50), nullable=True)

    # Estados
    estado_autorizado = Column(Boolean, nullable=True, default=False)
    estado_aprobado = Column(Boolean, nullable=True, default=False)
    estado_anulado = Column(Boolean, nullable=True, default=False)
    estado_apto = Column(Boolean, nullable=True, default=False)

    detalles = relationship(PoligonoDetalle, order_by=PoligonoDetalle.codigo_poligono_detalle_pk)
