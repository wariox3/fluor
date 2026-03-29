from pydantic import BaseModel
from typing import List, Optional


class SolicitudEmpleadoTipoResponse(BaseModel):
    codigo_solicitud_empleado_tipo_pk: str
    nombre: Optional[str]
    habilitado_portal: Optional[bool]

    model_config = {"from_attributes": True}


class SolicitudEmpleadoTipoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[SolicitudEmpleadoTipoResponse]
