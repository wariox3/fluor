from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.tenant_database import Base
from app.modules.crm.models.canal import Canal
from app.modules.crm.models.solicitud_tipo import SolicitudTipo
from app.modules.gen.models.tercero import Tercero


class Solicitud(Base):
    """Solicitud del CRM: las PQRS (peticiones, quejas, reclamos, sugerencias...) de los clientes."""

    __tablename__ = "crm_solicitud"

    codigo_solicitud_pk = Column(Integer, primary_key=True, index=True)
    codigo_solicitud_tipo_fk = Column(String(10), ForeignKey("crm_solicitud_tipo.codigo_solicitud_tipo_pk"), nullable=True, index=True)
    codigo_tercero_fk = Column(Integer, ForeignKey("gen_tercero.codigo_tercero_pk"), nullable=True, index=True)
    codigo_canal_fk = Column(String(10), ForeignKey("crm_canal.codigo_canal_pk"), nullable=True, index=True)

    # FKs sin modelo local
    codigo_ciudad_fk = Column(Integer, nullable=True)
    codigo_asesor_fk = Column(Integer, nullable=True)
    codigo_solicitud_tema_fk = Column(Integer, nullable=True)
    codigo_solicitud_origen_fk = Column(String(10), nullable=True)
    codigo_solicitud_receptor_fk = Column(Integer, nullable=True)
    codigo_receptor_responsable_fk = Column(Integer, nullable=True)
    codigo_area_fk = Column(String(10), nullable=True)
    codigo_riesgo_fk = Column(String(10), nullable=True)
    codigo_zona_fk = Column(String(20), nullable=True)

    descripcion = Column(Text, nullable=True)
    fecha = Column(Date, nullable=True)
    fecha_registro = Column(Date, nullable=True)
    fecha_vencimiento = Column(Date, nullable=True)
    fecha_respuesta = Column(Date, nullable=True)
    fecha_cierre = Column(Date, nullable=True)
    usuario = Column(String(50), nullable=True)
    recibido = Column(String(50), nullable=True)
    empresa = Column(String(100), nullable=True)
    habeas_data = Column(Boolean, nullable=False, default=False)

    # Contacto que registra la solicitud
    nombre_contacto = Column(String(80), nullable=True)
    numero_identificacion_contacto = Column(String(80), nullable=True)
    telefono_contacto = Column(String(50), nullable=True)
    celular_contacto = Column(String(50), nullable=True)
    correo_contacto = Column(String(100), nullable=True)
    cargo_contacto = Column(String(50), nullable=True)

    # Estados
    estado_autorizado = Column(Boolean, nullable=False, default=False)
    estado_aprobado = Column(Boolean, nullable=False, default=False)
    estado_anulado = Column(Boolean, nullable=False, default=False)
    estado_cerrado = Column(Boolean, nullable=False, default=False)

    # Relaciones
    solicitud_tipo_rel = relationship(SolicitudTipo, foreign_keys=[codigo_solicitud_tipo_fk])
    tercero_rel = relationship(Tercero, foreign_keys=[codigo_tercero_fk])
    canal_rel = relationship(Canal, foreign_keys=[codigo_canal_fk])

    @property
    def solicitud_tipo_nombre(self) -> str | None:
        return self.solicitud_tipo_rel.nombre if self.solicitud_tipo_rel else None

    @property
    def tercero_nombre_corto(self) -> str | None:
        return self.tercero_rel.nombre_corto if self.tercero_rel else None

    @property
    def canal_nombre(self) -> str | None:
        return self.canal_rel.nombre if self.canal_rel else None
