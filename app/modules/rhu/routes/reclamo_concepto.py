from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import func
from io import BytesIO
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.rhu.models.reclamo_concepto import ReclamoConcepto
from app.modules.rhu.schemas.reclamo_concepto import ReclamoConceptoListResponse

router = APIRouter()


@router.get("/lista", response_model=ReclamoConceptoListResponse)
def lista(page: int = 1, size: int = 50, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = db.query(ReclamoConcepto)
    total = query.with_entities(func.count(ReclamoConcepto.codigo_reclamo_concepto_pk)).scalar()
    offset = (page - 1) * size
    reclamos = query.offset(offset).limit(size).all()
    return ReclamoConceptoListResponse(total=total, page=page, size=size, items=reclamos)