from typing import List, Optional

from pydantic import BaseModel


class ClienteCondicionResponse(BaseModel):
    codigo_cliente_condicion_pk: int
    codigo_tercero_fk: Optional[int] = None
    tercero_nombre: Optional[str] = None
    codigo_condicion_fk: Optional[int] = None
    condicion_nombre: Optional[str] = None
    codigo_cliente_fk: Optional[int] = None

    model_config = {"from_attributes": True}


class ClienteCondicionListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[ClienteCondicionResponse]
