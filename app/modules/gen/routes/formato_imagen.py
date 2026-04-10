import base64
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.gen.models.formato_imagen import FormatoImagen
from app.modules.gen.schemas.formato_imagen import FormatoImagenListResponse, FormatoImagenResponse, FormatoImagenDetalleResponse, FormatoImagenActualizar, FormatoImagenActualizarItem, FormatoImagenListActualizarResponse

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

router = APIRouter()


@router.get("/{formato_imagen_id}/detalle", response_model=FormatoImagenDetalleResponse)
def detalle(
    formato_imagen_id: int,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    registro = db.query(FormatoImagen).filter(FormatoImagen.codigo_formato_imagen_pk == formato_imagen_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Imagen de formato no encontrada")
    imagen_base64 = None
    if registro.imagen:
        imagen_base64 = base64.b64encode(registro.imagen).decode("utf-8")
    return FormatoImagenDetalleResponse(
        codigo_formato_imagen_pk=registro.codigo_formato_imagen_pk,
        codigo_formato_fk=registro.codigo_formato_fk,
        imagen=imagen_base64,
        posicion_x=registro.posicion_x,
        posicion_y=registro.posicion_y,
        ancho=registro.ancho,
        alto=registro.alto,
        extension=registro.extension,
        visualizar_ultima_pagina=registro.visualizar_ultima_pagina,
    )


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


@router.patch("/{formato_imagen_id}/actualizar", response_model=FormatoImagenResponse)
def actualizar(
    formato_imagen_id: int,
    payload: FormatoImagenActualizar,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    registro = db.query(FormatoImagen).filter(FormatoImagen.codigo_formato_imagen_pk == formato_imagen_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Imagen de formato no encontrada")

    if payload.posicion_x is not None:
        registro.posicion_x = payload.posicion_x
    if payload.posicion_y is not None:
        registro.posicion_y = payload.posicion_y
    if payload.ancho is not None:
        registro.ancho = payload.ancho
    if payload.alto is not None:
        registro.alto = payload.alto

    db.commit()
    db.refresh(registro)
    return registro


@router.delete("/{formato_imagen_id}/eliminar", status_code=200)
def eliminar(
    formato_imagen_id: int,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    registro = db.query(FormatoImagen).filter(FormatoImagen.codigo_formato_imagen_pk == formato_imagen_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Imagen de formato no encontrada")
    db.delete(registro)
    db.commit()
    return {"mensaje": "Imagen eliminada correctamente"}


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


@router.get("/lista-actualizar", response_model=FormatoImagenListActualizarResponse)
def lista_actualizar(
    formato_id: int,
    page: int = 1,
    size: int = 50,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(FormatoImagen).filter(FormatoImagen.codigo_formato_fk == formato_id)
    total = query.with_entities(func.count(FormatoImagen.codigo_formato_imagen_pk)).scalar()
    offset = (page - 1) * size
    registros = query.offset(offset).limit(size).all()
    items = [
        FormatoImagenActualizarItem(
            codigo_formato_imagen_pk=r.codigo_formato_imagen_pk,
            codigo_formato_fk=r.codigo_formato_fk,
            imagen=base64.b64encode(r.imagen).decode("utf-8") if r.imagen else None,
            posicion_x=r.posicion_x,
            posicion_y=r.posicion_y,
            ancho=r.ancho,
            alto=r.alto,
            extension=r.extension,
            visualizar_ultima_pagina=r.visualizar_ultima_pagina,
        )
        for r in registros
    ]
    return FormatoImagenListActualizarResponse(total=total, page=page, size=size, items=items)
