from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List
from app.core.tenant_database import get_tenant_db
from app.modules.tte.models.guia import Guia
from app.modules.tte.schemas.guia import GuiaResponse, GuiaEstadoResponse

router = APIRouter()

@router.get("/lista", response_model=List[GuiaResponse])
def lista(page: int = 1, size: int = 50, db: Session = Depends(get_tenant_db)):
    offset = (page - 1) * size
    guias = (
        db.query(Guia)
        .offset(offset)
        .limit(size)
        .all()
    )

    return guias

@router.get("/estado/{guia}", response_model=GuiaEstadoResponse)
def estado(guia: int, db: Session = Depends(get_tenant_db)):
    guia = db.query(Guia).filter(Guia.codigo_guia_pk == guia).first()

    if not guia:
        raise HTTPException(status_code=404, detail="Guía no encontrada")

    return guia

@router.get("/estado-documento/{codigo_tercero}/{documento_cliente}", response_model=GuiaEstadoResponse)
def estado_documento(codigo_tercero: int, documento_cliente: str, db: Session = Depends(get_tenant_db)):

    stmt = (
        select(Guia)
        .where(
            Guia.codigo_tercero_fk == codigo_tercero,
            Guia.documento_cliente == documento_cliente
        )
        .limit(1)
    )

    guia = db.execute(stmt).scalar_one_or_none()

    if guia is None:
        raise HTTPException(status_code=404, detail="Guía no encontrada")

    return guia