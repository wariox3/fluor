from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.security import get_api_key
from app.core.tenant_database import get_tenant_db
from app.modules.tte.models.guia import Guia
from app.modules.tte.schemas.guia import GuiaResponse, GuiaEstadoResponse

router = APIRouter()

@router.get("/mensaje")
def test():
    return "Hola mundo desde la ruta de prueba!"

@router.get("/autenticar", response_model=GuiaEstadoResponse)
def autenticar(db: Session = Depends(get_tenant_db)):
    guia = db.query(Guia).filter(Guia.codigo_guia_pk == 6640798).first()

    if not guia:
        raise HTTPException(status_code=404, detail="Guía no encontrada")

    return guia