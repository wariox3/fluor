from sqlalchemy import Column, Integer, String, Date, Numeric
from app.core.tenant_database import Base

class Empleado(Base):
    __tablename__ = "rhu_empleado"

    codigo_empleado_pk = Column(Integer, primary_key=True, index=True)
    nombre_corto = Column(String(100), nullable=False)    
    correo = Column(String(100))
