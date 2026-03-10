from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Query, Session
from typing import List
from app.core.tenant_database import get_tenant_db
from app.modules.tte.models.guia import Guia
from app.modules.tte.schemas.guia import GuiaCreateRequest, GuiaResponse, GuiaEstadoResponse, GuiasMasivoRequest

router = APIRouter()

@router.post("/nuevo", response_model=GuiaEstadoResponse)
def nueva_guia(payload: GuiaCreateRequest, db: Session = Depends(get_tenant_db)):
    guia = Guia(
        codigo_guia_pk=payload.codigo_guia_pk,        
        codigo_guia_tipo_fk=payload.codigo_guia_tipo_fk,
        codigo_operacion_ingreso_fk=payload.codigo_operacion_ingreso_fk,
        codigo_operacion_cargo_fk=payload.codigo_operacion_ingreso_fk,  # Regla de negocio: cargo e ingreso inician con la misma operación; se diferencian en un proceso posterior
        codigo_tercero_fk=payload.codigo_tercero_fk,
        unidades=payload.unidades,
        peso_real=payload.peso_real,
        peso_volumen=payload.peso_volumen,
        vr_flete=payload.vr_flete,
        vr_manejo=payload.vr_manejo,
        vr_declara=payload.vr_declara,        
    )

    db.add(guia)
    db.commit()
    db.refresh(guia)

    return guia

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

@router.post("/estado-masivo", response_model=List[GuiaEstadoResponse])
def estado_masivo(payload: GuiasMasivoRequest, db: Session = Depends(get_tenant_db)):
    resultados = db.query(Guia).filter(Guia.codigo_guia_pk.in_(payload.guias)).all()

    if not resultados:
        raise HTTPException(status_code=404, detail="Ninguna guía encontrada")

    return resultados

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