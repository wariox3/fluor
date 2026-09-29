from pydantic import BaseModel


class CiudadResponse(BaseModel):
    codigo_ciudad_pk: int
    nombre: str

    model_config = {"from_attributes": True}


class CiudadListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[CiudadResponse]
       