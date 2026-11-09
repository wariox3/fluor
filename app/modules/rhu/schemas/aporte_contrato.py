from datetime import datetime

from pydantic import BaseModel


class AporteContratoPortalResponse(BaseModel):
    """Empleado del cliente incluido en la planilla de seguridad social del periodo."""

    codigo_aporte_contrato_pk: int
    codigo_aporte_fk: int
    codigo_contrato_fk: int
    codigo_empleado_fk: int | None = None
    empleado_nombre: str | None = None
    numero_identificacion: str | None = None
    # Soportes cargados en `doc_archivo`; 0 si aún no se ha cargado la planilla del empleado
    cantidad_archivos: int = 0


class AporteContratoPortalListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[AporteContratoPortalResponse]


class AporteContratoArchivoResponse(BaseModel):
    """Soporte de la planilla de seguridad social de un empleado."""

    codigo_archivo_pk: int
    nombre: str | None = None
    descripcion: str | None = None
    fecha: datetime | None = None
    extension_original: str | None = None
    tipo: str | None = None
    # Tamaño en bytes
    tamano: float | None = None

    model_config = {"from_attributes": True}
