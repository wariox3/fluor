from pydantic import BaseModel


class AreaResponse(BaseModel):
    codigo_area_pk: str
    nombre: str

    model_config = {"from_attributes": True}


class AreaListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[AreaResponse]
