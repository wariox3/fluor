from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.gen.models.ciudad import Ciudad


class Configuracion(Base):
    __tablename__ = "gen_configuracion"

    codigo_configuracion_pk = Column(Integer, primary_key=True, index=True)
    nit = Column(String(20))
    digito_verificacion = Column(String(2))
    nombre = Column(String(90))
    telefono = Column(String(25))
    direccion = Column(String(120))
    correo = Column(String(200))
    sitio_web = Column(String(120), nullable=True)
    logo = Column(LargeBinary, nullable=True)
    vr_auxilio_transporte = Column(Numeric(12, 2), nullable=True, default=0)
    codigo_empresa_fk = Column(Integer)
    codigo_ciudad_fk = Column(Integer, ForeignKey("gen_ciudad.codigo_ciudad_pk"), nullable=True)
    ruta_almacenamiento_servicio = Column(String(200), nullable=True)
    mostrar_programacion_impresion_pago = Column(Integer, nullable=True, default=1)
    mostrar_programacion = Column(Integer, nullable=True, default=1)

    ciudad_rel = relationship(Ciudad, foreign_keys=[codigo_ciudad_fk])
