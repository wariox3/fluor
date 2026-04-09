from sqlalchemy import Column, Integer, LargeBinary, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base


class FormatoImagen(Base):
    __tablename__ = "gen_formato_imagen"

    codigo_formato_imagen_pk = Column(Integer, primary_key=True, autoincrement=True)
    codigo_formato_fk = Column(Integer, ForeignKey("gen_formato.codigo_formato_pk"), nullable=False)
    imagen = Column(LargeBinary, nullable=True)
    posicion_x = Column(Integer, nullable=True, default=0)
    posicion_y = Column(Integer, nullable=True, default=0)
    ancho = Column(Integer, nullable=True, default=0)
    alto = Column(Integer, nullable=True, default=0)
    extension = Column(String(30), nullable=True)
    visualizar_ultima_pagina = Column(Boolean, nullable=False, default=False)

    formato_rel = relationship("Formato", back_populates="formatos_imagen_formato_rel")
