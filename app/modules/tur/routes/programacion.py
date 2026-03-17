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
	p.*,
	pu.nombre as puesto_nombre,
	pu.direccion as puesto_direccion,
	c.nombre as coordinador_nombre,
	pr.nombre as programador_nombre,
    pd.codigo_modalidad_fk,
    t.nombre_corto as tercero_nombre_corto                    
FROM
	tur_programacion p
LEFT JOIN tur_puesto pu ON p.codigo_puesto_fk = pu.codigo_puesto_pk 
LEFT JOIN tur_coordinador c ON pu.codigo_coordinador_fk = c.codigo_coordinador_pk
LEFT JOIN tur_programador pr ON pu.codigo_programador_fk = pr.codigo_programador_pk
LEFT JOIN tur_pedido_detalle pd ON p.codigo_pedido_detalle_fk = pd.codigo_pedido_detalle_pk
LEFT JOIN tur_pedido ped ON pd.codigo_pedido_fk = ped.codigo_pedido_pk
LEFT JOIN gen_tercero t ON ped.codigo_tercero_fk = t.codigo_tercero_pk
WHERE
	p.anio = :anio
	AND p.mes = :mes
	and p.codigo_empleado_fk = :empleado_id
""")

@router.get("/empleado", response_model=List[ProgramacionItem])
def cuenta(empleado_id: int, anio: int, mes: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user),):
    rows = db.execute(SQL_PROGRAMACION, {"empleado_id": empleado_id, "anio": anio, "mes":mes}).mappings().all()
    return [ProgramacionItem(**row) for row in rows]


