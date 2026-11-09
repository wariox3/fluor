from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String

from app.core.tenant_database import Base


class Archivo(Base):
    """
    Archivo documental heredado de holmio (`doc_archivo`).

    El contenido vive en Backblaze en
    `{gen_configuracion.ruta_almacenamiento_servicio}/archivo/{codigo_archivo_pk}.{extension_original}`.
    `codigo_archivo_tipo_fk` es el modelo dueño (p. ej. `RhuAporteContrato`) y `codigo` el id del
    registro dueño.
    """

    __tablename__ = "doc_archivo"

    codigo_archivo_pk = Column(Integer, primary_key=True, index=True)
    codigo_archivo_tipo_fk = Column(String(50), nullable=True, index=True)
    codigo = Column(String(50), nullable=True, index=True)
    # En holmio la propiedad se llama `fecha`, pero la columna es `fecha_hasta`
    fecha = Column("fecha_hasta", DateTime, nullable=True)
    nombre = Column(String(500), nullable=True)
    extension_original = Column(String(250), nullable=True)
    tipo = Column(String(250), nullable=True)
    tamano = Column(Float, nullable=True)
    descripcion = Column(String(100), nullable=True)
    usuario = Column(String(25), nullable=True)
    error_archivo = Column(Boolean, nullable=False, default=False)
    portal_clientes = Column(Boolean, nullable=False, default=False)
