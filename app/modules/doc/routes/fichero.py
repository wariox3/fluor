from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Query, Session
from typing import List
from app.core.tenant_database import get_tenant_db
from app.modules.doc.models.fichero import Fichero
from app.modules.doc.schemas.fichero import FicheroListResponse, FicheroResponse

router = APIRouter()

@router.get("/lista", response_model=FicheroListResponse)
def lista(page: int = 1, size: int = 50, db: Session = Depends(get_tenant_db)):
    total = db.query(func.count(Fichero.codigo_fichero_pk)).scalar()
    offset = (page - 1) * size
    ficheros = (
        db.query(Fichero)
        .offset(offset)
        .limit(size)
        .all()
    )
    return FicheroListResponse(total=total, page=page, size=size, items=ficheros)


@router.get("/modelo/{codigo_modelo}/{codigo}", response_model=List[FicheroResponse])
def modelo(codigo_modelo: str, codigo: str, db: Session = Depends(get_tenant_db)):
    ficheros = (
        db.query(Fichero)
        .filter(Fichero.codigo_modelo_fk == codigo_modelo, Fichero.codigo == codigo)
        .limit(10)
        .all()
    )
    return ficheros


