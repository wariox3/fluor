from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from app.core.master_database import get_master_db
from app.core.rate_limit import limiter
from app.core.tenant_database import get_tenant_engine
from app.core.security import get_current_user_from_token
from app.modules.auth.models.user import User
from app.modules.mas.models.tenant import Tenant
from app.modules.mas.models.user_tenant import UserTenant, es_control
from app.modules.rhu.models.empleado import Empleado
from app.modules.mas.schemas.user_tenant import (
    UserTenantAsociarRequest,
    UserTenantListResponse,
    UserTenantResponse,
    UserTenantUsuarioListResponse,
    UserTenantUsuarioResponse,
)

router = APIRouter()


@router.get("/lista", response_model=UserTenantListResponse, include_in_schema=False)
def lista(
    page: int = 1,
    size: int = 50,
    empleado: bool = False,
    db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user_from_token),
):
    """Empresas a las que pertenece el usuario autenticado. Con empleado=true, solo donde tiene empleado asignado."""
    usuario_id = int(current_user["sub"])
    query = db.query(UserTenant).filter(UserTenant.usuario_id == usuario_id)
    if empleado:
        query = query.filter(UserTenant.empleado_id.isnot(None))
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
            codigo_usuario_fk=ut.codigo_usuario_fk,
            activo=ut.activo,
            control=ut.control,
            erp=ut.erp,
            fecha_creacion=ut.fecha_creacion,
        )
        for ut, nombre in filas
    ]
    return UserTenantListResponse(total=total, page=page, size=size, items=items)


@router.get("/lista-tenant", response_model=UserTenantUsuarioListResponse, include_in_schema=False)
def lista_tenant(
    tenant_id: int,
    page: int = 1,
    size: int = 50,
    erp: bool | None = None,
    usuario_id: int | None = None,
    user_email: str | None = None,
    db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user_from_token),
):
    """Usuarios de una empresa. Solo para quien es control activo en ella.
    Filtros opcionales: erp, usuario_id y user_email (coincidencia parcial)."""
    if not es_control(db, int(current_user["sub"]), tenant_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para ver los usuarios de esta empresa")

    query = (
        db.query(UserTenant)
        .join(User, User.id == UserTenant.usuario_id)
        .filter(UserTenant.tenant_id == tenant_id)
    )
    if erp is not None:
        query = query.filter(UserTenant.erp == erp)
    if usuario_id is not None:
        query = query.filter(UserTenant.usuario_id == usuario_id)
    if user_email:
        query = query.filter(User.email.ilike(f"%{user_email.strip()}%"))
    total = query.with_entities(func.count(UserTenant.id)).scalar()
    offset = (page - 1) * size
    filas = (
        query.with_entities(UserTenant, User.email, User.nombres, User.apellidos)
        .order_by(User.nombres, User.apellidos, User.email)
        .offset(offset)
        .limit(size)
        .all()
    )
    items = [
        UserTenantUsuarioResponse(
            id=ut.id,
            usuario_id=ut.usuario_id,
            email=email,
            nombres=nombres,
            apellidos=apellidos,
            empleado_id=ut.empleado_id,
            codigo_usuario_fk=ut.codigo_usuario_fk,
            activo=ut.activo,
            control=ut.control,
            erp=ut.erp,
            fecha_creacion=ut.fecha_creacion,
        )
        for ut, email, nombres, apellidos in filas
    ]
    return UserTenantUsuarioListResponse(total=total, page=page, size=size, items=items)


@router.delete("/eliminar/{user_tenant_id}", include_in_schema=False)
def eliminar(
    user_tenant_id: int,
    db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user_from_token),
):
    """Elimina la asociación del usuario a una empresa. Solo el mismo usuario puede eliminar la suya."""
    user_tenant = db.query(UserTenant).filter(UserTenant.id == user_tenant_id).first()
    # Mismo 404 si no existe o es de otro usuario: no revela asociaciones ajenas
    if not user_tenant or user_tenant.usuario_id != int(current_user["sub"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asociación no encontrada")

    db.delete(user_tenant)
    db.commit()
    return {"detail": "Asociación eliminada correctamente"}


@router.post("/asociar", status_code=status.HTTP_201_CREATED, include_in_schema=False)
@limiter.limit("20/minute")
def asociar(
    request: Request,
    response: Response,
    data: UserTenantAsociarRequest,
    db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user_from_token),
):
    """Asocia al usuario autenticado a una empresa donde exista como empleado (mismo documento y correo)."""
    usuario_id = int(current_user["sub"])
    user = db.query(User).filter(User.id == usuario_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario no encontrado")

    # Si ya pertenece a la empresa (p. ej. por invitación) pero sin empleado, solo se completa el empleado
    existente = db.query(UserTenant).filter(
        UserTenant.usuario_id == usuario_id,
        UserTenant.tenant_id == data.tenant_id,
    ).first()
    if existente and existente.empleado_id is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya está asociado a esta empresa")

    tenant = db.query(Tenant).filter(Tenant.id == data.tenant_id).first()
    if not tenant or not tenant.schema:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empresa no encontrada")

    tenant_db = sessionmaker(bind=get_tenant_engine(tenant.schema))()
    try:
        empleado = tenant_db.query(Empleado).filter(
            Empleado.numero_identificacion == user.numero_identificacion,
            Empleado.correo == user.email,
        ).first()
    finally:
        tenant_db.close()

    if not empleado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró un empleado con ese número de identificación {user.numero_identificacion} y correo {user.email} en la empresa indicada",
        )

    if existente:
        existente.empleado_id = empleado.codigo_empleado_pk
        db.commit()
        response.status_code = status.HTTP_200_OK
        return {"detail": "Empleado asignado correctamente en la empresa"}

    db.add(UserTenant(
        usuario_id=usuario_id,
        tenant_id=data.tenant_id,
        empleado_id=empleado.codigo_empleado_pk,
        erp=False,
    ))
    try:
        db.commit()
    except IntegrityError:
        # Dos peticiones simultáneas: la restricción única (usuario, empresa) frena la segunda
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya está asociado a esta empresa")
    return {"detail": "Usuario asociado correctamente a la empresa"}
