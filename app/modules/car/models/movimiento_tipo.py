from sqlalchemy import Boolean, Column, Integer, String
from app.core.tenant_database import Base


class MovimientoTipo(Base):
    __tablename__ = "car_movimiento_tipo"

    codigo_movimiento_tipo_pk = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    consecutivo = Column(Integer, nullable=True, default=0)
    orden = Column(Integer, nullable=True, default=0)
    naturaleza = Column(String(1), nullable=True)
    prefijo = Column(String(20), nullable=True)
    codigo_empresa_fk = Column(Integer, nullable=False)

    # FKs sin modelo local
    codigo_comprobante_fk = Column(String, nullable=True)
    codigo_movimiento_clase_fk = Column(String(10), nullable=True)
    codigo_cuenta_cobrar_tipo_fk = Column(String(10), nullable=True)
    codigo_cuenta_fk = Column(String(20), nullable=True)

    genera_cuenta_cobrar = Column(Boolean, nullable=True, default=False)
    contabilizar = Column(Boolean, nullable=False, default=True)
