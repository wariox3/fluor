from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.gen.models.sucursal import Sucursal
from app.modules.gen.models.ciudad import Ciudad
from app.modules.gen.models.tercero import Tercero
from app.modules.gen.schemas.sucursal import SucursalListResponse, SucursalResponse

router = APIRouter()


@router.get("/lista", response_model=SucursalListResponse)
def lista(page: int = 1, size: int = 50, empresa_id: Optional[int] = None, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = (
        db.query(Sucursal, Ciudad.nombre.label("ciudad_nombre"), Tercero.nombre_corto.label("tercero_nombre_corto"), Tercero.numero_identificacion.label("tercero_numero_identificacion"))
        .outerjoin(Ciudad, Sucursal.codigo_ciudad_fk == Ciudad.codigo_ciudad_pk)
        .outerjoin(Tercero, Sucursal.codigo_tercero_fk == Tercero.codigo_tercero_pk)
    )
    if empresa_id:
        query = query.filter(Sucursal.codigo_empresa_fk == empresa_id)
    total = query.with_entities(func.count(Sucursal.codigo_sucursal_pk)).scalar()
    offset = (page - 1) * size
    rows = query.order_by(Sucursal.nombre).offset(offset).limit(size).all()
    items = []
    for sucursal, ciudad_nombre, tercero_nombre_corto, tercero_numero_identificacion in rows:
        item = SucursalResponse.model_validate(sucursal)
        item.ciudad_nombre = ciudad_nombre
        item.tercero_nombre_corto = tercero_nombre_corto
        item.tercero_numero_identificacion = tercero_numero_identificacion
        items.append(item)
    return SucursalListResponse(total=total, page=page, size=size, items=items)
