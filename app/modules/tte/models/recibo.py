from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.gen.models.tercero import Tercero
from app.modules.tte.models.guia import Guia
from app.modules.tte.models.operacion import Operacion


class Recibo(Base):
    __tablename__ = "tte_recibo"

    codigo_recibo_pk = Column(Integer, primary_key=True, index=True, autoincrement=True)
    numero = Column(Float, nullable=True, default=0.0)
    codigo_guia_fk = Column(Integer, ForeignKey("tte_guia.codigo_guia_pk"), nullable=True)
    codigo_operacion_fk = Column(String(20), ForeignKey("tte_operacion.codigo_operacion_pk"), nullable=True)
    codigo_tercero_fk = Column(Integer, ForeignKey("gen_tercero.codigo_tercero_pk"), nullable=True)
    fecha = Column(Date, nullable=True)
    vr_flete = Column(Float, nullable=False, default=0.0)
    vr_manejo = Column(Float, nullable=False, default=0.0)
    vr_total = Column(Float, nullable=False, default=0.0)
    estado_relacion = Column(Boolean, nullable=True, default=False)

    # FKs a otras entidades (sin modelo local)
    codigo_recibo_tipo_fk = Column(String(20), nullable=True)
    codigo_cliente_fk = Column(Integer, nullable=True)
    codigo_relacion_caja_fk = Column(Integer, nullable=True)

    # Relaciones
    guia = relationship(Guia, backref="recibos_guia")
    operacion = relationship(Operacion, backref="recibos_operacion")
    tercero = relationship(Tercero, backref="recibos_tercero")

    @property
    def tercero_nombre(self):
        return self.tercero.nombre_corto if self.tercero else None

    @property
    def operacion_nombre(self):
        return self.operacion.nombre if self.operacion else None
