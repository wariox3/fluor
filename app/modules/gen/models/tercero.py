from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from app.core.tenant_database import Base
from sqlalchemy.orm import relationship
from app.modules.gen.models.ciudad import Ciudad
from app.modules.gen.models.asesor import Asesor
from app.modules.tte.models.condicion import Condicion

class Tercero(Base):
    __tablename__ = "gen_tercero"

    codigo_tercero_pk = Column(Integer, primary_key=True, index=True)
    nombre_corto = Column(String)
    numero_identificacion = Column(String)
    direccion = Column(String)
    telefono = Column(String)
    correo = Column(String)
    critico = Column(Boolean)
    cliente = Column(Boolean)
    proveedor = Column(Boolean)
    empleado = Column(Boolean)
    prospecto = Column(Boolean)
    permanente = Column(Boolean)
    estado_inactivo = Column(Boolean)
    codigo_ciudad_fk = Column(String(20), ForeignKey("gen_ciudad.codigo_ciudad_pk"))
    codigo_forma_pago_fk = Column(String(10), nullable=True)
    codigo_asesor_fk = Column(Integer, ForeignKey("gen_asesor.codigo_asesor_pk"), nullable=True)
    codigo_condicion_fk = Column(Integer, ForeignKey("tte_condicion.codigo_condicion_pk"), nullable=True)

    ciudad = relationship(Ciudad, foreign_keys=[codigo_ciudad_fk], backref="terceros_ciudad_rel")
    asesor = relationship(Asesor, foreign_keys=[codigo_asesor_fk], backref="terceros_asesor_rel")
    condicion = relationship(Condicion, foreign_keys=[codigo_condicion_fk], backref="terceros_condicion_rel")

    @hybrid_property
    def ciudad_nombre(self):
        return self.ciudad.nombre if self.ciudad else None

    @hybrid_property
    def asesor_nombre(self):
        return self.asesor.nombre if self.asesor else None

    @hybrid_property
    def condicion_nombre(self):
        return self.condicion.nombre if self.condicion else None

    @hybrid_property
    def condicion_codigo_precio_fk(self):
        return self.condicion.codigo_precio_fk if self.condicion else None
