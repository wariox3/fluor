from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.tte.models.despacho import Despacho
from app.modules.tte.models.guia import Guia


class DespachoDetalle(Base):
    __tablename__ = "tte_despacho_detalle"

    codigo_despacho_detalle_pk = Column(Integer, primary_key=True, index=True)
    codigo_despacho_fk = Column(Integer, ForeignKey("tte_despacho.codigo_despacho_pk"), nullable=True)
    codigo_guia_fk = Column(Integer, ForeignKey("tte_guia.codigo_guia_pk"), nullable=True)

    # Pesos y unidades
    unidades = Column(Float, nullable=False, default=0.0)
    peso_real = Column(Float, nullable=False, default=0.0)
    peso_volumen = Column(Float, nullable=False, default=0.0)
    peso_costo = Column(Float, nullable=False, default=0.0)

    # Valores
    vr_declara = Column(Float, nullable=False, default=0.0)
    vr_flete = Column(Float, nullable=False, default=0.0)
    vr_manejo = Column(Float, nullable=False, default=0.0)
    vr_otros = Column(Float, nullable=False, default=0.0)
    vr_recaudo = Column(Float, nullable=False, default=0.0)
    vr_contra_entrega = Column(Float, nullable=False, default=0.0)
    vr_costo = Column(Float, nullable=True, default=0.0)
    vr_costo_flete = Column(Float, nullable=True, default=0.0)
    vr_costo_otros = Column(Float, nullable=False, default=0.0)
    vr_costo_unidades = Column(Float, nullable=True, default=0.0)
    vr_cobro_entrega = Column(Float, nullable=False, default=0.0)
    vr_precio_reexpedicion = Column(Float, nullable=False, default=0.0)

    # Porcentajes
    porcentaje_participacion_costo = Column(Float, nullable=False, default=0.0)
    porcentaje_rentabilidad = Column(Float, nullable=False, default=0.0)

    # Validación y flags
    unidades_validacion = Column(Integer, nullable=False, default=0)
    adicional = Column(Boolean, nullable=True, default=False)
    redespacho = Column(Boolean, nullable=False, default=False)

    # Relaciones
    despacho = relationship(Despacho, foreign_keys=[codigo_despacho_fk], backref="despachos_detalles_despacho")
    guia = relationship(Guia, foreign_keys=[codigo_guia_fk], backref="despachos_detalles_guia")
