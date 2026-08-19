from typing import List, Optional

from pydantic import BaseModel


class ProductoResponse(BaseModel):
    codigo_producto_pk: str
    nombre: Optional[str]

    model_config = {"from_attributes": True}


class ProductoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[ProductoResponse]
