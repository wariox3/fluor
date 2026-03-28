from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.master_database import get_master_db
from app.modules.auth.models.tenant import Tenant
from app.modules.auth.schemas.tenant import TenantResponse, TenantListResponse

router = APIRouter()


@router.get("/lista", response_model=TenantListResponse)
def lista(page: int = 1, size: int = 50, db: Session = Depends(get_master_db)):
    query = db.query(Tenant)
    total = query.with_entities(func.count(Tenant.id)).scalar()
    offset = (page - 1) * size
    tenants = query.order_by(Tenant.nombre).offset(offset).limit(size).all()
    items = [TenantResponse(id=t.id, nombre=t.nombre, schema_=t.schema) for t in tenants]
    return TenantListResponse(total=total, page=page, size=size, items=items)
