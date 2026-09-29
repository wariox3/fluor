from pydantic import BaseModel


class SubareaResponse(BaseModel):
    codigo_subarea_pk: str
    nombre: str

    model_config = {"from_attributes": True}


class SubareaListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[SubareaResponse]
