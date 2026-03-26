from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base


class Empleado(Base):
    __tablename__ = "rhu_empleado"

    codigo_empleado_pk = Column(Integer, primary_key=True, index=True)
    nombre_corto = Column(String(100), nullable=False)
    numero_identificacion = Column(String(20))
    correo = Column(String(100))
    cuenta = Column(String(80), nullable=True)
    codigo_banco_fk = Column(String(10), ForeignKey("rhu_banco.codigo_banco_pk"), nullable=True)
    codigo_zona_fk = Column(String(10), ForeignKey("rhu_zona.codigo_zona_pk"), nullable=True)

    banco_rel = relationship("Banco", foreign_keys=[codigo_banco_fk])
    zona_rel = relationship("Zona", foreign_keys=[codigo_zona_fk])
