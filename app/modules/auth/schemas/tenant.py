from pydantic import BaseModel
from typing import List


class TenantResponse(BaseModel):
    id: int
    nombre: str | None

    model_config = {"from_attributes": True}


class TenantListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[TenantResponse]
