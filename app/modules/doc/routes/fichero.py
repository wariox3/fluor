from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.orm import Query, Session
from typing import List
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.core.backblaze import b2_client
from app.modules.doc.models import fichero
from app.modules.doc.models.fichero import Fichero
from app.modules.doc.schemas.fichero import FicheroListResponse, FicheroResponse

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
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al descargar el fichero desde el almacenamiento")

    nombre_archivo = f"{fichero.nombre}.{fichero.extension}"
    return Response(
        content=contenido,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{nombre_archivo}"'},
    )


