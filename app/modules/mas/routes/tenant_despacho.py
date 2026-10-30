import hmac
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from app.core.master_database import get_master_db
from app.core.rate_limit import limiter
from app.core.tenant_database import get_tenant_engine
from app.core.security import get_current_user_from_token
from app.modules.mas.models.tenant import Tenant
from app.modules.mas.models.tenant_despacho import TenantDespacho
from app.modules.tte.models.despacho import Despacho
from app.modules.mas.schemas.tenant_despacho import TenantDespachoCargarRequest, TenantDespachoResponse

router = APIRouter()


def _respuesta(asignacion: TenantDespacho, tenant: Tenant) -> TenantDespachoResponse:
    return TenantDespachoResponse(
        id=asignacion.id,
        fecha=asignacion.fecha,
        tenant_id=asignacion.tenant_id,
        tenant_nombre=tenant.nombre,
        codigo_despacho=asignacion.codigo_despacho_fk,
    )


@router.post("/cargar", response_model=TenantDespachoResponse, include_in_schema=False)
@limiter.limit("5/minute")
def cargar(
    request: Request,
    response: Response,
    data: TenantDespachoCargarRequest,
    db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user_from_token),
):
    """Asigna un despacho al repartidor autenticado validando el api_token del despacho."""
    usuario_id = int(current_user["sub"])
    # Mismo error para empresa, despacho o token inválidos: no revela qué existe
    invalido = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Despacho o token no válido")

    tenant = db.query(Tenant).filter(Tenant.id == data.tenant_id, Tenant.activo == True).first()
    if not tenant or not tenant.schema:
        raise invalido

    tenant_db = sessionmaker(bind=get_tenant_engine(tenant.schema))()
    try:
        despacho = tenant_db.query(Despacho).filter(Despacho.codigo_despacho_pk == data.codigo_despacho).first()
        token_valido = (
            despacho is not None
            and despacho.api_token
            and hmac.compare_digest(despacho.api_token.encode(), data.api_token.encode())
        )
        if not token_valido or despacho.estado_anulado or despacho.estado_cerrado or despacho.estado_entregado:
            raise invalido
    finally:
        tenant_db.close()

    filtro = (TenantDespacho.tenant_id == tenant.id, TenantDespacho.codigo_despacho_fk == data.codigo_despacho)
    existente = db.query(TenantDespacho).filter(*filtro).first()
    if existente:
        if existente.usuario_id != usuario_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El despacho ya está asignado a otro repartidor")
        return _respuesta(existente, tenant)

    asignacion = TenantDespacho(usuario_id=usuario_id, tenant_id=tenant.id, codigo_despacho_fk=data.codigo_despacho)
    db.add(asignacion)
    try:
        db.commit()
    except IntegrityError:
        # Otra petición lo asignó al mismo tiempo
        db.rollback()
        existente = db.query(TenantDespacho).filter(*filtro).first()
        if existente and existente.usuario_id == usuario_id:
            return _respuesta(existente, tenant)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El despacho ya está asignado a otro repartidor")
    db.refresh(asignacion)
    return _respuesta(asignacion, tenant)
