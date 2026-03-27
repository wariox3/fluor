from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text, func
from typing import List, Optional
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tur.models.programacion import Programacion
from app.modules.tur.models.pedido import Pedido
from app.modules.tur.schemas.programacion import ProgramacionItem, ProgramacionListResponse, ProgramacionResponse

router = APIRouter()

@router.get("/lista", response_model=ProgramacionListResponse)
def lista(page: int = 1, size: int = 50, empleado_id: Optional[int] = None, tercero_id: Optional[int] = None, anio: Optional[int] = None, mes: Optional[int] = None, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = db.query(Programacion)
    if empleado_id:
        query = query.filter(Programacion.codigo_empleado_fk == empleado_id)
    if tercero_id:
        query = query.join(Pedido, Programacion.codigo_pedido_fk == Pedido.codigo_pedido_pk).filter(Pedido.codigo_tercero_fk == tercero_id)
    if anio:
        query = query.filter(Programacion.anio == anio)
    if mes:
        query = query.filter(Programacion.mes == mes)
    total = query.with_entities(func.count(Programacion.codigo_programacion_pk)).scalar()
    offset = (page - 1) * size
    items = (
        query
        .options(
            joinedload(Programacion.puesto_rel),
            joinedload(Programacion.empleado_rel),
        )
        .order_by(Programacion.codigo_programacion_pk.desc())
        .offset(offset)
        .limit(size)
        .all()
    )
    return ProgramacionListResponse(
        total=total, page=page, size=size,
        items=[ProgramacionResponse.from_orm_with_rels(i) for i in items]
    )


@router.get("/empleado", response_model=List[ProgramacionItem])
def empleado(empleado_id: int, anio: int, mes: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user),):
    sql = text("""
        SELECT
            p.*,
            pu.nombre as puesto_nombre,
            pu.direccion as puesto_direccion,
            c.nombre as coordinador_nombre,
            pr.nombre as programador_nombre,
            pd.codigo_modalidad_fk,
            t.nombre_corto as tercero_nombre_corto
        FROM tur_programacion p
        LEFT JOIN tur_puesto pu ON p.codigo_puesto_fk = pu.codigo_puesto_pk
        LEFT JOIN tur_coordinador c ON pu.codigo_coordinador_fk = c.codigo_coordinador_pk
        LEFT JOIN tur_programador pr ON pu.codigo_programador_fk = pr.codigo_programador_pk
        LEFT JOIN tur_pedido_detalle pd ON p.codigo_pedido_detalle_fk = pd.codigo_pedido_detalle_pk
        LEFT JOIN tur_pedido ped ON pd.codigo_pedido_fk = ped.codigo_pedido_pk
        LEFT JOIN gen_tercero t ON ped.codigo_tercero_fk = t.codigo_tercero_pk
        WHERE p.anio = :anio AND p.mes = :mes AND p.codigo_empleado_fk = :empleado_id
    """)
    rows = db.execute(sql, {"empleado_id": empleado_id, "anio": anio, "mes": mes}).mappings().all()
    return [ProgramacionItem(**row) for row in rows]


