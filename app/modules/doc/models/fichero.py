from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime, Numeric, Float
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.gen.models.tercero import Tercero
from app.modules.tte.models.guia_tipo import GuiaTipo
from app.modules.tte.models.operacion import Operacion

class Fichero(Base):
    __tablename__ = "doc_fichero"

    codigo_fichero_pk = Column(Integer, primary_key=True, index=True)
    codigo_fichero_tipo_fk = Column(String(1))
    codigo_modelo_fk = Column(String(80))
    codigo = Column(String(50))
    fecha = Column(DateTime)
    nombre = Column(String(500))
    extension = Column(String(20))
    tipo = Column(String(100))
    ui = Column(String(3))
    comprimido = Column(Boolean, default=False)
    tamano = Column(Float)
    usuario = Column(String(25))
    directorio_base = Column(String(150))
    error_carga = Column(Boolean, default=False)
