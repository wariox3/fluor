from pydantic import BaseModel
from typing import List, Optional


class ItemResponse(BaseModel):
    codigo_item_pk: int
    nombre: Optional[str] = None

    model_config = {"from_attributes": True}


class ItemListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[ItemResponse]
       