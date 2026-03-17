from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.gen.models.item import Item
from app.modules.gen.schemas.item import ItemListResponse

router = APIRouter()

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