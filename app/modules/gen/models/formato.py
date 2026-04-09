from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base


class Formato(Base):
    __tablename__ = "gen_formato"

    codigo_formato_pk = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=True)
    titulo = Column(String(300), nullable=True)
    contenido = Column(Text, nullable=True)
    contenido_externo = Column(Text, nullable=True)
    etiquetas = Column(Text, nullable=True)
    tamano_papel = Column(String(10), nullable=True)
    orientacion_papel = Column(String(1), nullable=True)
    tamanio_fuente = Column(String(20), nullable=True)
    nombre_firma = Column(String(100), nullable=True)
    cargo_firma = Column(String(150), nullable=True)
    nombre_firma_otro = Column(String(100), nullable=True)
    cargo_firma_otro = Column(String(150), nullable=True)
    nombre_firma_otro_dos = Column(String(100), nullable=True)
    cargo_firma_otro_dos = Column(String(150), nullable=True)
    nombre_empresa = Column(Boolean, nullable=True)
    nit_empresa = Column(Boolean, nullable=True)
    huella = Column(Boolean, nullable=True)
    codigo_modelo_fk = Column(String(80), nullable=True)
    version = Column(String(20), nullable=True)
    codigo = Column(String(20), nullable=True)

    formatos_imagen_formato_rel = relationship("FormatoImagen", back_populates="formato_rel")
