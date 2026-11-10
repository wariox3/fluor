from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String

from app.core.tenant_database import Base


class VisitaCompromiso(Base):
    __tablename__ = "crm_visita_compromiso"

    # En la tabla la llave se llama `codigo_visita_pk` (así la creó holmio)
    codigo_visita_compromiso_pk = Column("codigo_visita_pk", Integer, primary_key=True, index=True)
    codigo_visita_fk = Column(Integer, ForeignKey("crm_visita.codigo_visita_pk"), nullable=True, index=True)
    nombre = Column(String(50), nullable=False)
    detalle = Column(String(800), nullable=True)
    fecha = Column(Date, nullable=True)
    estado_atendido = Column(Boolean, nullable=False, default=False)
    # Si el compromiso es del cliente (True) o de la empresa (False)
    cliente = Column(Boolean, nullable=False, default=False)
