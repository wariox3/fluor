from sqlalchemy import Column, ForeignKey, Integer, String
from app.core.master_database import Base


class UserTenantConfiguracion(Base):
    """Configuración que el control de la empresa asigna a un usuario en esa empresa (1 a 1 con mas_user_tenant)."""
    __tablename__ = "mas_user_tenant_configuracion"

    id = Column(Integer, primary_key=True)
    user_tenant_id = Column(Integer, ForeignKey("mas_user_tenant.id", ondelete="CASCADE"), nullable=False, unique=True)
    # Datos de la base de la empresa (otra base: sin FK)
    codigo_operacion_fk = Column(String(20), nullable=True)
    codigo_tercero_operacion_fk = Column(Integer, nullable=True)
    codigo_ciudad_origen_fk = Column(String(20), nullable=True)
