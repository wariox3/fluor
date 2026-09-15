from fastapi import APIRouter, Depends, HTTPException, Query
import calendar
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text, func
from typing import List, Optional
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.tur.models.programacion import Programacion
from app.modules.tur.models.pedido import Pedido
from app.modules.tur.models.pedido_detalle import PedidoDetalle
from app.modules.tur.models.puesto import Puesto
from app.modules.rhu.models.contrato import Contrato
from app.modules.gen.models.configuracion import Configuracion
from app.modules.tur.schemas.programacion import ProgramacionItem, ProgramacionListResponse, ProgramacionResponse, ProgramacionDiaItem

router = APIRouter()

@router.get("/lista", response_model=ProgramacionListResponse)
def lista(page: int = 1, size: int = 50, empleado_id: Optional[int] = None, tercero_id: Optional[int] = None, codigo_puesto_fk: Optional[int] = None, anio: Optional[int] = None, mes: Optional[int] = None, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = db.query(Programacion)
    if empleado_id:
        query = query.filter(Programacion.codigo_empleado_fk == empleado_id)
    if codigo_puesto_fk:
        query = query.filter(Programacion.codigo_puesto_fk == codigo_puesto_fk)
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
            joinedload(Programacion.puesto_rel).joinedload(Puesto.zona_rel),
            joinedload(Programacion.puesto_rel).joinedload(Puesto.subzona_rel),
            joinedload(Programacion.empleado_rel),
            joinedload(Programacion.contrato_rel).joinedload(Contrato.cargo_rel),
            joinedload(Programacion.contrato_rel).joinedload(Contrato.grupo_rel),
            joinedload(Programacion.pedido_detalle_rel).joinedload(PedidoDetalle.pedido_rel).joinedload(Pedido.tercero_rel),
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
    mostrar_programacion = db.query(Configuracion.mostrar_programacion).scalar()
    if not mostrar_programacion:
        return []
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




@router.get("/dia", response_model=List[ProgramacionDiaItem])
def dia(anio: int, mes: int = Query(..., ge=1, le=12), dia: int = Query(..., ge=1, le=31), codigo_zona_fk: Optional[str] = None, codigo_cargo_fk: Optional[str] = None, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    if dia > calendar.monthrange(anio, mes)[1]:
        raise HTTPException(status_code=400, detail=f"El mes {mes} de {anio} no tiene dia {dia}")
    # dia ya está validado como entero 1-31, por lo que es seguro interpolar el nombre de columna
    columna = f"dia_{dia}"
    params = {"anio": anio, "mes": mes}
    filtros = ""
    if codigo_zona_fk:
        filtros += " AND pu.codigo_zona_fk = :codigo_zona_fk"
        params["codigo_zona_fk"] = codigo_zona_fk
    if codigo_cargo_fk:
        filtros += " AND co.codigo_cargo_fk = :codigo_cargo_fk"
        params["codigo_cargo_fk"] = codigo_cargo_fk
    sql = text(f"""
        SELECT
            p.codigo_programacion_pk,
            p.codigo_empleado_fk,
            e.nombre_corto as empleado_nombre,
            e.numero_identificacion as empleado_numero_identificacion,
            e.celular as empleado_celular,
            p.codigo_contrato_fk,
            co.codigo_cargo_fk,
            ca.nombre as cargo_nombre,
            co.codigo_grupo_fk,
            g.nombre as grupo_nombre,
            p.codigo_puesto_fk,
            pu.nombre as puesto_nombre,
            pu.codigo_zona_fk,
            z.nombre as zona_nombre,
            t.nombre_corto as tercero_nombre_corto,
            p.{columna} as codigo_turno,
            tu.nombre as turno_nombre,
            tu.hora_desde,
            tu.hora_hasta,
            tu.horas,
            p.complementario,
            p.adicional
        FROM tur_programacion p
        LEFT JOIN rhu_empleado e ON p.codigo_empleado_fk = e.codigo_empleado_pk
        LEFT JOIN rhu_contrato co ON p.codigo_contrato_fk = co.codigo_contrato_pk
        LEFT JOIN rhu_cargo ca ON co.codigo_cargo_fk = ca.codigo_cargo_pk
        LEFT JOIN rhu_grupo g ON co.codigo_grupo_fk = g.codigo_grupo_pk
        LEFT JOIN tur_puesto pu ON p.codigo_puesto_fk = pu.codigo_puesto_pk
        LEFT JOIN tur_zona z ON pu.codigo_zona_fk = z.codigo_zona_pk
        LEFT JOIN tur_pedido_detalle pd ON p.codigo_pedido_detalle_fk = pd.codigo_pedido_detalle_pk
        LEFT JOIN tur_pedido ped ON pd.codigo_pedido_fk = ped.codigo_pedido_pk
        LEFT JOIN gen_tercero t ON ped.codigo_tercero_fk = t.codigo_tercero_pk
        LEFT JOIN tur_turno tu ON p.{columna} = tu.codigo_turno_pk
        WHERE p.anio = :anio AND p.mes = :mes AND p.{columna} IS NOT NULL AND p.{columna} <> ''{filtros}
        ORDER BY pu.nombre, e.nombre_corto
    """)
    rows = db.execute(sql, params).mappings().all()
    return [ProgramacionDiaItem(**row) for row in rows]
