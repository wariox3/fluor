from datetime import datetime

from pydantic import BaseModel


class ArchivoResponse(BaseModel):
    """Archivo documental heredado de holmio (`doc_archivo`)."""

    codigo_archivo_pk: int
    nombre: str | None = None
    descripcion: str | None = None
    fecha: datetime | None = None
    extension_original: str | None = None
    tipo: str | None = None
    # Tamaño en bytes
    tamano: float | None = None

    model_config = {"from_attributes": True}
