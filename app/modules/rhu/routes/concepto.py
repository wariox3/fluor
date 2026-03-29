from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.rhu.models.concepto import Concepto
from app.modules.rhu.schemas.concepto import ConceptoListResponse

router = APIRouter()


@router.get("/lista", response_model=ConceptoListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    nombre: Optional[str] = None,
    credito: Optional[bool] = None,
    embargo: Optional[bool] = None,
    adicional: Optional[bool] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Concepto)

    if nombre:
        query = query.filter(Concepto.nombre.ilike(f"%{nombre}%"))
    if credito is not None:
        query = query.filter(Concepto.credito == credito)
    if embargo is not None:
        query = query.filter(Concepto.embargo == embargo)
    if adicional is not None:
        query = query.filter(Concepto.adicional == adicional)

    total = query.with_entities(func.count(Concepto.codigo_concepto_pk)).scalar()
    offset = (page - 1) * size
    items = query.order_by(Concepto.orden.asc(), Concepto.nombre.asc()).offset(offset).limit(size).all()

    return ConceptoListResponse(total=total, page=page, size=size, items=items)
