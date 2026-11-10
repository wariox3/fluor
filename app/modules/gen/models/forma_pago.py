from sqlalchemy import Column, String

from app.core.tenant_database import Base


class FormaPago(Base):
    __tablename__ = "gen_forma_pago"

    codigo_forma_pago_pk = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(50), nullable=True)
