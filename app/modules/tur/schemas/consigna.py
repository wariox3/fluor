from pydantic import BaseModel
from typing import List, Optional


class ConsignaResponse(BaseModel):
    codigo_consigna_pk: int
    codigo_puesto_fk: Optional[int]
    puesto_nombre: Optional[str]
    codigo_empresa_fk: int
    consigna: Optional[str]
    habilitado_portal: Optional[bool]

    model_config = {"from_attributes": True}


class ConsignaListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[ConsignaResponse]
