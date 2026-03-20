from pydantic import BaseModel
from typing import List


class ProgramacionReporteTipoResponse(BaseModel):
    codigo_programacion_reporte_tipo_pk: str
    nombre: str

    class Config:
        from_attributes = True


class ProgramacionReporteTipoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[ProgramacionReporteTipoResponse]
