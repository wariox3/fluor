from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.gen.models.formato_imagen import FormatoImagen
from app.modules.gen.schemas.formato_imagen import FormatoImagenListResponse, FormatoImagenResponse

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

router = APIRouter()


@router.post("/nuevo", response_model=FormatoImagenResponse, status_code=201)
async def nuevo(
    codigo_formato_fk: int = Form(...),
    posicion_x: int = Form(0),
    posicion_y: int = Form(0),
    ancho: int = Form(0),
    alto: int = Form(0),
    visualizar_ultima_pagina: bool = Form(False),
    imagen: UploadFile = File(...),
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    nombre_original = imagen.filename or ""
    extension = nombre_original.rsplit(".", 1)[-1].lower() if "." in nombre_original else ""
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Solo se permiten imágenes jpg o png")

    data = await imagen.read()
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="El archivo está vacío")

    registro = FormatoImagen(
        codigo_formato_fk=codigo_formato_fk,
        imagen=data,
        posicion_x=posicion_x,
        posicion_y=posicion_y,
        ancho=ancho,
        alto=alto,
        extension=extension,
        visualizar_ultima_pagina=visualizar_ultima_pagina,
    )
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro


@router.get("/lista", response_model=FormatoImagenListResponse)
def lista(
    page: int = 1,
    size: int = 50,
    formato_id: Optional[int] = None,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(FormatoImagen)
    if formato_id:
        query = query.filter(FormatoImagen.codigo_formato_fk == formato_id)
    total = query.with_entities(func.count(FormatoImagen.codigo_formato_imagen_pk)).scalar()
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    return FormatoImagenListResponse(total=total, page=page, size=size, items=items)
