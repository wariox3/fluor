import magic
import re
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import Response
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.core.backblaze import b2_client
from app.modules.doc.models.fichero import Fichero
from app.modules.doc.schemas.fichero import FicheroListResponse, FicheroResponse
from app.modules.gen.models.configuracion import Configuracion

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "doc", "docx", "xls", "xlsx"}

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

router = APIRouter()

@router.get("/lista", response_model=FicheroListResponse)
def lista(page: int = 1, size: int = 50, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
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
def modelo(codigo_modelo: str, codigo: str, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    ficheros = (
        db.query(Fichero)
        .filter(Fichero.codigo_modelo_fk == codigo_modelo, Fichero.codigo == codigo)
        .limit(10)
        .all()
    )
    return ficheros

@router.get("/descargar/{fichero_id}")
def descargar(fichero_id: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    fichero = db.query(Fichero).filter(Fichero.codigo_fichero_pk == fichero_id).first()
    if not fichero:
        raise HTTPException(status_code=404, detail="Fichero no encontrado")
    directorio = {"F": "firma", "I": "imagen"}.get(fichero.codigo_fichero_tipo_fk, "fichero")
    ruta = f"{fichero.directorio_base}/{directorio}/{fichero.codigo_fichero_pk}.{fichero.extension}"

    try:
        contenido, content_type = b2_client.download_file(ruta)
    except Exception:
        raise HTTPException(status_code=502, detail="Error al descargar el fichero desde el almacenamiento")

    nombre_archivo = f"{fichero.nombre}.{fichero.extension}"
    return Response(
        content=contenido,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{nombre_archivo}"'},
    )

@router.get("/descargar-url/{fichero_id}")
def descargar_url(fichero_id: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    fichero = db.query(Fichero).filter(Fichero.codigo_fichero_pk == fichero_id).first()
    if not fichero:
        raise HTTPException(status_code=404, detail="Fichero no encontrado")
    directorio = {"F": "firma", "I": "imagen"}.get(fichero.codigo_fichero_tipo_fk, "fichero")
    ruta = f"{fichero.directorio_base}/{directorio}/{fichero.codigo_fichero_pk}.{fichero.extension}"
    url = b2_client.get_download_url(ruta)
    return {"url": url}


@router.post("/cargar/{codigo_modelo}/{codigo}", status_code=201)
async def cargar(
    codigo_modelo: str,
    codigo: str,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    max_file_size = 10 * 1024 * 1024  # 10 MB
    if not archivo.filename:
        raise HTTPException(status_code=400, detail="No se envió ningún archivo")

    data = await archivo.read()
    if len(data) == 0 or len(data) > max_file_size:
        raise HTTPException(status_code=400, detail="El archivo supera el tamaño máximo permitido de 10MB")

    nombre_original = archivo.filename or ""
    extension = nombre_original.rsplit(".", 1)[-1].lower() if "." in nombre_original else ""

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Tipo de archivo no permitido")

    mime_real = magic.from_buffer(data[:2048], mime=True)
    if mime_real not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="El contenido del archivo no corresponde a un tipo permitido")

    nombre_original = re.sub(r"[^\w.\-]", "_", nombre_original)
    mime_type = mime_real

    configuracion = db.query(Configuracion).first()
    if not configuracion or not configuracion.ruta_almacenamiento_servicio:
        raise HTTPException(status_code=500, detail="No está configurada la ruta del servicio documental")

    directorio_base = configuracion.ruta_almacenamiento_servicio
    nuevo = Fichero(
        codigo_fichero_tipo_fk='G',
        codigo_modelo_fk=codigo_modelo,
        codigo=codigo,
        fecha=datetime.now(),
        nombre=nombre_original,
        extension=extension,
        tipo=mime_type,
        tamano=len(data),
        usuario="portal",
        directorio_base=directorio_base,
    )
    db.add(nuevo)
    db.flush()  # populate codigo_fichero_pk before upload

    ruta = f"{directorio_base}/fichero/{nuevo.codigo_fichero_pk}.{extension}"

    try:
        b2_client.upload_file(ruta, data, mime_type)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=502, detail="Error al subir el fichero al almacenamiento")

    db.commit()
    db.refresh(nuevo)
    return {"codigo_fichero_pk": nuevo.codigo_fichero_pk}
