from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from app.core.tenant_database import Base
from sqlalchemy.orm import relationship

class Negocio(Base):
    __tablename__ = "crm_negocio"

    codigo_negocio_pk = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    