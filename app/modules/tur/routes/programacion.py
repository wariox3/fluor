from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tur.schemas.programacion import ProgramacionItem

router = APIRouter()

SQL_PROGRAMACION = text("""
SELECT
	p.*
FROM
	tur_programacion p
WHERE
	p.anio = :anio
	AND p.mes = :mes
	and p.codigo_empleado_fk = :empleado_id
""")

@router.get("/empleado", response_model=List[ProgramacionItem])
def cuenta(empleado_id: int, anio: int, mes: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user),):
    rows = db.execute(SQL_PROGRAMACION, {"empleado_id": empleado_id, "anio": anio, "mes":mes}).mappings().all()
    return [ProgramacionItem(**row) for row in rows]


