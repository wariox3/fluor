from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.tenant_database import Base
from app.modules.crm.models.visita_compromiso import VisitaCompromiso
from app.modules.crm.models.visita_motivo import VisitaMotivo
from app.modules.crm.models.visita_reporte import VisitaReporte
from app.modules.crm.models.visita_tipo import VisitaTipo
from app.modules.gen.models.asesor import Asesor
from app.modules.gen.models.tercero import Tercero


class Visita(Base):
    __tablename__ = "crm_visita"

    codigo_visita_pk = Column(Integer, primary_key=True, index=True)
    codigo_visita_tipo_fk = Column(String(20), ForeignKey("crm_visita_tipo.codigo_visita_tipo_pk"), nullable=True, index=True)
    codigo_visita_motivo_fk = Column(String(20), ForeignKey("crm_visita_motivo.codigo_visita_motivo_pk"), nullable=True, index=True)
    codigo_tercero_fk = Column(Integer, ForeignKey("gen_tercero.codigo_tercero_pk"), nullable=True, index=True)
    codigo_asesor_fk = Column(Integer, ForeignKey("gen_asesor.codigo_asesor_pk"), nullable=True, index=True)

    # FKs sin modelo local
    codigo_prospecto_fk = Column(Integer, nullable=True)
    codigo_negocio_fk = Column(Integer, ForeignKey("crm_negocio.codigo_negocio_pk"), nullable=True)

    fecha = Column(DateTime, nullable=True)
    fecha_programada = Column(DateTime, nullable=True)
    comentarios = Column(String(2000), nullable=True)

    # Estados
    estado_autorizado = Column(Boolean, nullable=False, default=False)
    estado_aprobado = Column(Boolean, nullable=False, default=False)
    estado_anulado = Column(Boolean, nullable=False, default=False)

    # Relaciones
    visita_tipo_rel = relationship(VisitaTipo, foreign_keys=[codigo_visita_tipo_fk])
    visita_motivo_rel = relationship(VisitaMotivo, foreign_keys=[codigo_visita_motivo_fk])
    asesor_rel = relationship(Asesor, foreign_keys=[codigo_asesor_fk])
    tercero_rel = relationship(Tercero, foreign_keys=[codigo_tercero_fk])
    # Como holmio, en el orden en que se registraron
    compromisos = relationship(VisitaCompromiso, order_by=VisitaCompromiso.codigo_visita_compromiso_pk)
    reportes = relationship(VisitaReporte, order_by=VisitaReporte.codigo_visita_reporte_pk)

    @property
    def visita_tipo_nombre(self) -> str | None:
        return self.visita_tipo_rel.nombre if self.visita_tipo_rel else None

    @property
    def visita_motivo_nombre(self) -> str | None:
        return self.visita_motivo_rel.nombre if self.visita_motivo_rel else None

    @property
    def asesor_nombre(self) -> str | None:
        return self.asesor_rel.nombre if self.asesor_rel else None

    @property
    def tercero_nombre_corto(self) -> str | None:
        return self.tercero_rel.nombre_corto if self.tercero_rel else None
