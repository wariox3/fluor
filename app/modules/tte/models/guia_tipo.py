from sqlalchemy import Column, String
from app.core.tenant_database import Base

class GuiaTipo(Base):
    __tablename__ = "tte_guia_tipo"

    codigo_guia_tipo_pk = Column(String(20), primary_key=True, index=True)            
    nombre = Column(String)
