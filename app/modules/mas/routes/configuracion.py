from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.master_database import get_master_db
from app.core.security import get_current_user
from app.modules.mas.models.configuracion import Configuracion
from app.modules.mas.schemas.configuracion import ConfiguracionResponse, ConfiguracionActualizar

router = APIRouter()


@router.get("", response_model=ConfiguracionResponse)
def obtener(
    db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user),
):
    config = db.query(Configuracion).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    return config


@router.patch("", response_model=ConfiguracionResponse)
def actualizar(
    datos: ConfiguracionActualizar,
    db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user),
):
    config = db.query(Configuracion).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    config.tasa_interes = datos.tasa_interes
    db.commit()
    db.refresh(config)
    return config
