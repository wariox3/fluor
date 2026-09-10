from typing import List, Optional

from pydantic import BaseModel


class TerceroProductoResponse(BaseModel):
    codigo_tercero_producto_pk: int
    codigo_tercero_fk: Optional[int] = None
    tercero_nombre: Optional[str] = None
    codigo_producto_fk: Optional[str] = None
    producto_nombre: Optional[str] = None

    model_config = {"from_attributes": True}


class TerceroProductoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[TerceroProductoResponse]
