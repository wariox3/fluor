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

class ItemCreate(BaseModel):
    nombre: Optional[str]    
    codigo_impuesto_retencion_fk: str
    codigo_impuesto_retencion_compra_fk: str
    codigo_impuesto_iva_venta_fk: str
    codigo_impuesto_iva_compra_fk: str    
    afecta_inventario: bool
    producto: bool
    venta: bool
    compra: bool
       