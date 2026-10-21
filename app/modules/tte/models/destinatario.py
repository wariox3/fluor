from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from app.core.tenant_database import Base
from app.modules.gen.models.identificacion import Identificacion
from app.modules.gen.models.tercero import Tercero
from app.modules.tte.models.ciudad import Ciudad


class Destinatario(Base):
    __tablename__ = "tte_destinatario"

    codigo_destinatario_pk = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo_identificacion_fk = Column(String(3), ForeignKey("gen_identificacion.codigo_identificacion_pk"), nullable=True)
    codigo_ciudad_fk = Column(String(20), ForeignKey("tte_ciudad.codigo_ciudad_pk"), nullable=True)
    codigo_tercero_fk = Column(Integer, ForeignKey("gen_tercero.codigo_tercero_pk"), nullable=True)
    codigo_empresa_fk = Column(Integer, nullable=False)

    numero_identificacion = Column(String(20), nullable=True)
    digito_verificacion = Column(String(1), nullable=True)
    nombre_corto = Column(String(150), nullable=True)
    nombre1 = Column(String(50), nullable=True)
    nombre2 = Column(String(50), nullable=True)
    apellido1 = Column(String(50), nullable=True)
    apellido2 = Column(String(50), nullable=True)
    direccion = Column(String(200), nullable=True)
    telefono = Column(String(30), nullable=True)
    movil = Column(String(30), nullable=True)
    correo = Column(String(1000), nullable=True)
    comentario = Column(String(2000), nullable=True)
    estado_inactivo = Column(Boolean, nullable=True, default=False)

    identificacion = relationship(Identificacion, foreign_keys=[codigo_identificacion_fk], backref="destinatarios_identificacion_rel")
    ciudad = relationship(Ciudad, foreign_keys=[codigo_ciudad_fk], backref="destinatarios_ciudad_rel")
    tercero = relationship(Tercero, foreign_keys=[codigo_tercero_fk], backref="destinatarios_tercero_rel")

    @hybrid_property
    def identificacion_nombre(self):
        return self.identificacion.nombre if self.identificacion else None

    @hybrid_property
    def ciudad_nombre(self):
        return self.ciudad.nombre if self.ciudad else None

    @hybrid_property
    def tercero_nombre(self):
        return self.tercero.nombre_corto if self.tercero else None
