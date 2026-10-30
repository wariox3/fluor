from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint, func
from app.core.master_database import Base


class TenantDespacho(Base):
    """Despacho de una empresa asignado a un usuario (repartidor) para la app móvil."""
    __tablename__ = "mas_tenant_despacho"
    __table_args__ = (UniqueConstraint("tenant_id", "codigo_despacho_fk", name="uq_tenant_despacho_tenant_despacho"),)

    id                 = Column(Integer, primary_key=True)
    fecha              = Column(DateTime, server_default=func.now(), nullable=False)
    usuario_id         = Column(Integer, ForeignKey("auth_user.id"), nullable=False, index=True)
    tenant_id          = Column(Integer, ForeignKey("mas_tenant.id"), nullable=False, index=True)
    # tte_despacho.codigo_despacho_pk en la base de la empresa (otra base: sin FK)
    codigo_despacho_fk = Column(Integer, nullable=False)
