from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.core.config import DEFAULT_EMPRESA_ID
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.gen.models.item import Item
from app.modules.gen.schemas.item import ItemListResponse, ItemResponse, ItemCreate

router = APIRouter()

@router.post("/nuevo", response_model=ItemResponse)
def nuevo(data: ItemCreate, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    item = Item(
        nombre=data.nombre,
        codigo_impuesto_retencion_fk=data.codigo_impuesto_retencion_fk,
        codigo_impuesto_retencion_compra_fk=data.codigo_impuesto_retencion_compra_fk,
        codigo_impuesto_iva_venta_fk=data.codigo_impuesto_iva_venta_fk,
        codigo_impuesto_iva_compra_fk=data.codigo_impuesto_iva_compra_fk,
        afecta_inventario=data.afecta_inventario,
        producto=data.producto,
        venta=data.venta,
        compra=data.compra,
        codigo_empresa_fk=DEFAULT_EMPRESA_ID,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("/lista", response_model=ItemListResponse)
def lista(page: int = 1, size: int = 50, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    total = db.query(func.count(Item.codigo_item_pk)).scalar()
    offset = (page - 1) * size
    items = (
        db.query(Item)
        .offset(offset)
        .limit(size)
        .all()
    )
    return ItemListResponse(total=total, page=page, size=size, items=items)