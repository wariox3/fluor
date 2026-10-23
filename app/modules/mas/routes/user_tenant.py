from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.master_database import get_master_db
from app.core.security import get_current_user_from_token
from app.modules.mas.models.tenant import Tenant
from app.modules.mas.models.user_tenant import UserTenant
from app.modules.mas.schemas.user_tenant import UserTenantResponse, UserTenantListResponse

router = APIRouter()


@router.get("/lista", response_model=UserTenantListResponse, include_in_schema=False)
def lista(
    page: int = 1,
    size: int = 50,
    db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user_from_token),
):
    """Empresas a las que pertenece el usuario autenticado."""
    usuario_id = int(current_user["sub"])
    query = db.query(UserTenant).filter(UserTenant.usuario_id == usuario_id)
    total = query.with_entities(func.count(UserTenant.id)).scalar()
    offset = (page - 1) * size
    filas = (
        query.join(Tenant, Tenant.id == UserTenant.tenant_id)
        .with_entities(UserTenant, Tenant.nombre)
        .order_by(Tenant.nombre)
        .offset(offset)
        .limit(size)
        .all()
    )
    items = [
        UserTenantResponse(
            id=ut.id,
            tenant_id=ut.tenant_id,
            tenant_nombre=nombre,
            empleado_id=ut.empleado_id,
            activo=ut.activo,
            control=ut.control,
            fecha_creacion=ut.fecha_creacion,
        )
        for ut, nombre in filas
    ]
    return UserTenantListResponse(total=total, page=page, size=size, items=items)
