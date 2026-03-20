from pydantic import BaseModel
from typing import List


class PagoTipoResponse(BaseModel):
    codigo_pago_tipo_pk: str
    nombre: str

    class Config:
        from_attributes = True


class PagoTipoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[PagoTipoResponse]
