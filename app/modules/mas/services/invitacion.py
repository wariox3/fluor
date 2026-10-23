from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased

from app.modules.auth.models.user import User
from app.modules.mas.models.invitacion import EstadoInvitacion, Invitacion
from app.modules.mas.models.tenant import Tenant
from app.modules.mas.models.user_tenant import UserTenant, es_control


def crear(db: Session, usuario_id: int, tenant_id: int, usuario_invitado_id: int) -> Invitacion:
    """Crea una invitación pendiente. Solo puede invitar quien es control activo en la empresa."""
    if not es_control(db, usuario_id, tenant_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para invitar usuarios a esta empresa")

    invitado = db.query(User).filter(User.id == usuario_invitado_id).first()
    if not invitado or not invitado.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    if not invitado.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no ha verificado su cuenta")

    if _pertenece(db, usuario_invitado_id, tenant_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya pertenece a esta empresa")

    pendiente = db.query(Invitacion.id).filter(
        Invitacion.usuario_invitado_id == usuario_invitado_id,
        Invitacion.tenant_id == tenant_id,
        Invitacion.estado == EstadoInvitacion.pendiente,
    ).first()
    if pendiente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya tiene una invitación pendiente a esta empresa")

    invitacion = Invitacion(tenant_id=tenant_id, usuario_id=usuario_id, usuario_invitado_id=usuario_invitado_id)
    db.add(invitacion)
    db.commit()
    db.refresh(invitacion)
    return invitacion


def listar_pendientes(db: Session, usuario_id: int, page: int, size: int) -> tuple[int, list[dict]]:
    """Invitaciones pendientes dirigidas al usuario, con el nombre de la empresa y de quien invitó."""
    query = db.query(Invitacion).filter(
        Invitacion.usuario_invitado_id == usuario_id,
        Invitacion.estado == EstadoInvitacion.pendiente,
    )
    total = query.with_entities(func.count(Invitacion.id)).scalar()
    filas = (
        query.join(Tenant, Tenant.id == Invitacion.tenant_id)
        # outer join: quien invitó puede haber sido eliminado (usuario_id en null)
        .outerjoin(User, User.id == Invitacion.usuario_id)
        .with_entities(Invitacion, Tenant.nombre, User.nombres, User.apellidos, User.email)
        .order_by(Invitacion.fecha.desc(), Invitacion.id.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    items = [
        {
            "id": inv.id,
            "tenant_id": inv.tenant_id,
            "tenant_nombre": tenant_nombre,
            "usuario_id": inv.usuario_id,
            "usuario_nombre": " ".join(p for p in (nombres, apellidos) if p) or None,
            "usuario_email": email,
            "fecha": inv.fecha,
        }
        for inv, tenant_nombre, nombres, apellidos, email in filas
    ]
    return total, items


def listar_tenant(
    db: Session, usuario_id: int, tenant_id: int, estado: EstadoInvitacion | None, page: int, size: int
) -> tuple[int, list[dict]]:
    """Invitaciones enviadas por una empresa, opcionalmente filtradas por estado. Solo para quien es control activo en ella."""
    if not es_control(db, usuario_id, tenant_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para ver las invitaciones de esta empresa")

    invitado = aliased(User)
    invitador = aliased(User)
    query = db.query(Invitacion).filter(Invitacion.tenant_id == tenant_id)
    if estado is not None:
        query = query.filter(Invitacion.estado == estado)
    total = query.with_entities(func.count(Invitacion.id)).scalar()
    filas = (
        query.join(invitado, invitado.id == Invitacion.usuario_invitado_id)
        # outer join: quien invitó puede haber sido eliminado (usuario_id en null)
        .outerjoin(invitador, invitador.id == Invitacion.usuario_id)
        .with_entities(
            Invitacion,
            invitado.nombres, invitado.apellidos, invitado.email,
            invitador.nombres, invitador.apellidos, invitador.email,
        )
        .order_by(Invitacion.fecha.desc(), Invitacion.id.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    items = [
        {
            "id": inv.id,
            "usuario_invitado_id": inv.usuario_invitado_id,
            "usuario_invitado_nombre": " ".join(p for p in (inv_nombres, inv_apellidos) if p) or None,
            "usuario_invitado_email": inv_email,
            "usuario_id": inv.usuario_id,
            "usuario_nombre": " ".join(p for p in (nombres, apellidos) if p) or None,
            "usuario_email": email,
            "estado": inv.estado,
            "fecha": inv.fecha,
        }
        for inv, inv_nombres, inv_apellidos, inv_email, nombres, apellidos, email in filas
    ]
    return total, items


def aceptar(db: Session, invitacion_id: int, usuario_id: int) -> Invitacion:
    """Acepta la invitación: crea el acceso en user_tenant y la marca como aceptada."""
    invitacion = _pendiente_del_usuario(db, invitacion_id, usuario_id)
    if _pertenece(db, usuario_id, invitacion.tenant_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya perteneces a esta empresa")

    # Acceso y cambio de estado en una sola transacción
    db.add(UserTenant(usuario_id=usuario_id, tenant_id=invitacion.tenant_id))
    invitacion.estado = EstadoInvitacion.aceptada
    try:
        db.commit()
    except IntegrityError:
        # Otra petición creó el acceso al mismo tiempo (restricción única usuario–empresa)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya perteneces a esta empresa")
    db.refresh(invitacion)
    return invitacion


def rechazar(db: Session, invitacion_id: int, usuario_id: int) -> Invitacion:
    """Rechaza la invitación; solo cambia su estado."""
    invitacion = _pendiente_del_usuario(db, invitacion_id, usuario_id)
    invitacion.estado = EstadoInvitacion.rechazada
    db.commit()
    db.refresh(invitacion)
    return invitacion


def _pertenece(db: Session, usuario_id: int, tenant_id: int) -> bool:
    return db.query(UserTenant.id).filter(
        UserTenant.usuario_id == usuario_id,
        UserTenant.tenant_id == tenant_id,
    ).first() is not None


def _pendiente_del_usuario(db: Session, invitacion_id: int, usuario_id: int) -> Invitacion:
    """Invitación pendiente dirigida al usuario. 404 si no existe o es de otro, para no revelar invitaciones ajenas."""
    invitacion = db.query(Invitacion).filter(
        Invitacion.id == invitacion_id,
        Invitacion.usuario_invitado_id == usuario_id,
    ).first()
    if not invitacion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitación no encontrada")
    if invitacion.estado != EstadoInvitacion.pendiente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"La invitación ya fue {invitacion.estado.value}")
    return invitacion
