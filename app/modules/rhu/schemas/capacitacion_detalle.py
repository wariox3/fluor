from pydantic import BaseModel, model_validator
from typing import Any, List, Optional
from datetime import datetime
from app.modules.gen.schemas.enlace import EnlaceResponse
from app.modules.doc.schemas.fichero import FicheroResponse


class CapacitacionDetalleResponse(BaseModel):
    codigo_capacitacion_detalle_pk: int
    codigo_capacitacion_fk: int
    evaluacion: Optional[str] = None
    asistencia: bool
    capacitacion_objetivo: Optional[str] = None
    capacitacion_fecha_capacitacion: Optional[datetime] = None
    capacitacion_lugar: Optional[str] = None
    capacitacion_contenido: Optional[str] = None
    enlaces: List[EnlaceResponse] = []
    ficheros: List[FicheroResponse] = []

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def flatten_capacitacion(cls, data: Any):
        cap = getattr(data, "capacitacion_rel", None)
        if cap:
            data.__dict__.update({
                "capacitacion_objetivo": cap.objetivo,
                "capacitacion_fecha_capacitacion": cap.fecha_capacitacion,
                "capacitacion_lugar": cap.lugar,
                "capacitacion_contenido": cap.contenido,
            })
        return data


class CapacitacionDetalleListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[CapacitacionDetalleResponse]
