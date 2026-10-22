from sqlalchemy import Boolean, Column, String
from app.core.tenant_database import Base

class GuiaTipo(Base):
    __tablename__ = "tte_guia_tipo"

    codigo_guia_tipo_pk = Column(String(20), primary_key=True, index=True)            
    nombre = Column(String)
    genera_cobro = Column(Boolean, nullable=True, default=False)
    codigo_pago_fk = Column(String(3), nullable=True)
    codigo_forma_pago = Column(String(3), nullable=True)
    validar_flete = Column(Boolean, nullable=True, default=False)
    mensaje_formato = Column(String(900), nullable=True)
