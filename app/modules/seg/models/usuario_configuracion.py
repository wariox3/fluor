from sqlalchemy import Boolean, Column, Float, String

from app.core.tenant_database import Base


class UsuarioConfiguracion(Base):
    __tablename__ = "seg_usuario_configuracion"

    username_pk = Column(String(25), primary_key=True, index=True, autoincrement=False)
    porcentaje_manejo_minimo = Column(Float, nullable=True, default=0.0)
    manejo_minimo_unidad = Column(Float, nullable=True, default=0.0)
    manejo_minimo_despacho = Column(Float, nullable=True, default=0.0)
    descuento_peso_maximo = Column(Float, nullable=True, default=0.0)
    restringir_guia_nueva = Column(Boolean, nullable=True, default=False)
    cambiar_valores_guia = Column(Boolean, nullable=False, default=False)
