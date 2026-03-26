from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
from sqlalchemy.ext.hybrid import hybrid_property
from app.core.tenant_database import Base
from sqlalchemy.orm import relationship

class ImpuestoTipo(Base):
    __tablename__ = "gen_impuesto_tipo"

    codigo_impuesto_tipo_pk = Column(String(3), primary_key=True, index=True)
    nombre = Column(String)