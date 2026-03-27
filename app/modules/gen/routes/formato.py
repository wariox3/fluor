from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.gen.models.formato import Formato
from app.modules.gen.schemas.formato import FormatoListResponse, FormatoResponse, FormatoContenidoUpdate

router = APIRouter()


@router.get("/lista", response_model=FormatoListResponse)
def lista(page: int = 1, size: int = 50, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    total = db.query(func.count(Formato.codigo_formato_pk)).scalar()
    offset = (page - 1) * size
    formatos = (
        db.query(Formato)
        .offset(offset)
        .limit(size)
        .all()
    )
    return FormatoListResponse(total=total, page=page, size=size, items=formatos)


@router.get("/{formato_id}", response_model=FormatoResponse)
def detalle(formato_id: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    formato = db.query(Formato).filter(Formato.codigo_formato_pk == formato_id).first()
    if not formato:
        raise HTTPException(status_code=404, detail="Formato no encontrado")
    return formato


@router.patch("/{formato_id}/contenido")
def actualizar_contenido(formato_id: int, body: FormatoContenidoUpdate, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    formato = db.query(Formato).filter(Formato.codigo_formato_pk == formato_id).first()
    if not formato:
        raise HTTPException(status_code=404, detail="Formato no encontrado")
    formato.contenido_externo = body.contenido_externo
    db.commit()
    return {"ok": True}
