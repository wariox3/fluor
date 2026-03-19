from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.rhu.models.contrato import Contrato
from app.modules.rhu.schemas.contrato import ContratoListResponse

router = APIRouter()


@router.get("/lista", response_model=ContratoListResponse)
def lista(page: int = 1, size: int = 50, empleado_id: Optional[str] = None, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = db.query(Contrato)
    if empleado_id:
        query = query.filter(Contrato.codigo_empleado_fk == empleado_id)
    total = query.with_entities(func.count(Contrato.codigo_contrato_pk)).scalar()
    offset = (page - 1) * size
    contratos = query.offset(offset).limit(size).all()
    return ContratoListResponse(total=total, page=page, size=size, items=contratos)