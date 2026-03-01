from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.modules.tte.models.guia import Guia
from app.modules.tte.schemas.guia import GuiaResponse

router = APIRouter()

@router.get("/", response_model=List[GuiaResponse])
def listar_guias(db: Session = Depends(get_db)):
    return db.query(Guia).all()