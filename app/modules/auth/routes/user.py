import logging
from app.core.rate_limit import limiter
from fastapi import APIRouter, HTTPException, status, Depends, Request, Response
from sqlalchemy.orm import Session, aliased
from typing import Optional
from app.core.security import require_admin, get_current_user, get_current_user_from_token, verify_password
from app.core.master_database import get_master_db
from app.modules.auth.models.user import User, UserRole
from app.modules.auth.models.verificacion import Verificacion, TipoVerificacion, EstadoVerificacion
from app.modules.auth.schemas.user import UserResponse, RegisterRequest, RegisterResponse, RecuperarClaveRequest, RestablecerClaveRequest, ReenviarVerificacionRequest, ActualizarPerfilRequest, PerfilResponse, EliminarCuentaRequest
from app.core.security import hash_password, generate_verification_token
from app.core.config import DEBUG
from app.core.utils import frontend_url
from app.core.zinc import Zinc
from app.core.turnstile import verify_turnstile
from sqlalchemy import func, or_
from app.modules.auth.schemas.user import UserListResponse, UserSeleccionarListResponse
from app.modules.mas.models.user_tenant import UserTenant
from app.modules.mas.models.tenant import Tenant

logger = logging.getLogger(__name__)

router = APIRouter()

# Tipos de verificación de cuenta (registro inicial + reenvíos)
TIPOS_VERIFICACION = (TipoVerificacion.registro, TipoVerificacion.reenvio)


def _client_ip(request: Request) -> Optional[str]:
    return request.client.host if request.client else None

@router.get("/lista", response_model=UserListResponse, include_in_schema=False)
def lista(page: int = 1, size: int = 50, email: Optional[str] = None,role: Optional[str] = None, is_verified: Optional[bool] = None,db: Session = Depends(get_master_db),current_user: dict = Depends(require_admin)
):
    query = db.query(User)
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    if role:
        query = query.filter(User.role == role)
    if is_verified is not None:
        query = query.filter(User.is_verified == is_verified)
    total = query.count()
    offset = (page - 1) * size
    users = query.order_by(User.id.asc()).offset(offset).limit(size).all()
    return UserListResponse(total=total, page=page, size=size, items=users)

@router.get("/seleccionar", response_model=UserSeleccionarListResponse, include_in_schema=False)
@limiter.limit("60/minute")
def seleccionar(request: Request, response: Response, page: int = 1, size: int = 50, buscar: Optional[str] = None, db: Session = Depends(get_master_db), current_user: dict = Depends(get_current_user)):
    """Usuarios activos y verificados, con datos básicos. Cualquier usuario autenticado puede consultarlo."""
    query = db.query(User).filter(User.is_active == True, User.is_verified == True)
    if buscar:
        patron = f"%{buscar}%"
        query = query.filter(or_(User.email.ilike(patron), User.nombres.ilike(patron), User.apellidos.ilike(patron)))
    total = query.with_entities(func.count(User.id)).scalar()
    offset = (page - 1) * size
    users = query.order_by(User.nombres, User.apellidos, User.email).offset(offset).limit(size).all()
    return UserSeleccionarListResponse(total=total, page=page, size=size, items=users)

@router.get("/detalle", response_model=PerfilResponse, include_in_schema=False)
def detalle(db: Session = Depends(get_master_db), current_user: dict = Depends(get_current_user)):
    user = db.query(User).filter(User.id == int(current_user.get("sub"))).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user


@router.post("/registrar", response_model=RegisterResponse, response_model_exclude_none=True, include_in_schema=False)
@limiter.limit("3/minute")
def registrar(request: Request, response: Response, data: RegisterRequest, db: Session = Depends(get_master_db)):
    # Turnstile solo aplica al front web; móvil y api no pueden resolverlo
    if data.client_type == "web":
        verify_turnstile(data.turnstile_token)

    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya está registrado"
        )
    token = generate_verification_token()
    new_user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        nombres=data.nombres,
        apellidos=data.apellidos,
        numero_identificacion=data.numero_identificacion,
        role=UserRole.employee,
        is_verified=False,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    db.add(Verificacion(
        usuario_id=new_user.id,
        tipo=TipoVerificacion.registro,
        token=token,
        ip=_client_ip(request),
    ))
    db.commit()

    verification_link = f"{frontend_url(request.headers.get('origin'))}/auth/verify-email?token={token}"

    html_content = f"""
        <h1>¡Hola {new_user.nombres}!</h1>
        <p>Estamos comprometidos con la seguridad. Por favor verifica tu cuenta haciendo clic en el siguiente enlace.</p>
        <a href='{verification_link}'>Verificar cuenta</a>
    """
    try:
        Zinc().correo(new_user.email, "Verifica tu cuenta", html_content)
    except Exception as e:
        logger.warning(f"No se pudo enviar correo de verificación a {new_user.email}: {e}")

    return RegisterResponse(
        user=UserResponse.model_validate(new_user),
        verification_link=verification_link if DEBUG else None,
    )


@router.post("/recuperar-clave", include_in_schema=False)
@limiter.limit("3/minute")
def recuperar_clave(request: Request, response: Response, data: RecuperarClaveRequest, db: Session = Depends(get_master_db)):
    # Turnstile solo aplica al front web; móvil y api no pueden resolverlo
    if data.client_type == "web":
        verify_turnstile(data.turnstile_token)

    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        return {"detail": "Si el correo existe, recibirás las instrucciones para recuperar tu clave"}
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Cuenta no verificada", "is_verified": False}
        )
    
    if user:
        token = generate_verification_token()
        db.add(Verificacion(
            usuario_id=user.id,
            tipo=TipoVerificacion.recuperacion,
            token=token,
            ip=_client_ip(request),
        ))
        db.commit()
        reset_link = f"{frontend_url(request.headers.get('origin'))}/auth/restablecer-clave?token={token}"
        html_content = f"""
            <h1>Recuperación de clave</h1>
            <p>Recibimos una solicitud para restablecer la clave de tu cuenta.</p>
            <p>Haz clic en el siguiente enlace para crear una nueva clave:</p>
            <a href='{reset_link}'>Restablecer clave</a>
            <p>Si no solicitaste esto, ignora este correo.</p>
        """
        try:
            Zinc().correo(user.email, "Recuperación de clave", html_content)
        except Exception as e:
            logger.warning(f"No se pudo enviar correo de recuperación a {user.email}: {e}")
    return {"detail": "Si el correo existe, recibirás las instrucciones para recuperar tu clave"}


@router.post("/restablecer-clave", include_in_schema=False)
@limiter.limit("5/minute")
def restablecer_clave(request: Request, response: Response, data: RestablecerClaveRequest, db: Session = Depends(get_master_db)):
    # Turnstile solo aplica al front web; móvil y api no pueden resolverlo
    if data.client_type == "web":
        verify_turnstile(data.turnstile_token)

    verificacion = db.query(Verificacion).filter(
        Verificacion.token == data.token,
        Verificacion.tipo == TipoVerificacion.recuperacion,
        Verificacion.estado == EstadoVerificacion.pendiente,
    ).first()
    if not verificacion:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido o expirado")
    user = db.query(User).filter(User.id == verificacion.usuario_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido o expirado")
    user.password_hash = hash_password(data.nueva_clave)
    verificacion.estado = EstadoVerificacion.usado
    verificacion.fecha_uso = func.now()
    db.commit()
    return {"detail": "Clave restablecida correctamente"}


@router.get("/verificar", include_in_schema=False)
@limiter.limit("10/minute")
def verificar(request: Request, response: Response, token: str, db: Session = Depends(get_master_db)):
    verificacion = db.query(Verificacion).filter(
        Verificacion.token == token,
        Verificacion.tipo.in_(TIPOS_VERIFICACION),
        Verificacion.estado == EstadoVerificacion.pendiente,
    ).first()
    if not verificacion:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido")
    user = db.query(User).filter(User.id == verificacion.usuario_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido")
    if user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cuenta ya verificada")
    user.is_verified = True
    verificacion.estado = EstadoVerificacion.usado
    verificacion.fecha_uso = func.now()
    db.commit()
    return {"detail": "Cuenta verificada correctamente"}

@router.post("/reenviar-verificacion", include_in_schema=False)
@limiter.limit("1/minute")
def reenviar_verificacion(request: Request, response: Response, data: ReenviarVerificacionRequest, db: Session = Depends(get_master_db)):
    # Turnstile solo aplica al front web; móvil y api no pueden resolverlo
    if data.client_type == "web":
        verify_turnstile(data.turnstile_token)

    user = db.query(User).filter(User.email == data.email).first()
    if user and not user.is_verified:
        token = generate_verification_token()
        db.add(Verificacion(
            usuario_id=user.id,
            tipo=TipoVerificacion.reenvio,
            token=token,
            ip=_client_ip(request),
        ))
        db.commit()
        verification_link = f"{frontend_url(request.headers.get('origin'))}/auth/verify-email?token={token}"
        html_content = f"""
            <h1>¡Hola {user.nombres}!</h1>
            <p>Solicitaste reenviar el correo de verificación. Haz clic en el siguiente enlace para verificar tu cuenta.</p>
            <a href='{verification_link}'>Verificar cuenta</a>
        """
        try:
            Zinc().correo(user.email, "Verifica tu cuenta", html_content)
        except Exception as e:
            logger.warning(f"No se pudo reenviar correo de verificación a {user.email}: {e}")
    return {"detail": "Si el correo existe y la cuenta no está verificada, recibirás el enlace de verificación"}


@router.put("/actualizar", response_model=UserResponse, include_in_schema=False)
def actualizar(data: ActualizarPerfilRequest, db: Session = Depends(get_master_db), current_user: dict = Depends(get_current_user)):
    user = db.query(User).filter(User.id == int(current_user.get("sub"))).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    user.nombres = data.nombres
    user.apellidos = data.apellidos
    user.numero_identificacion = data.numero_identificacion
    db.commit()
    db.refresh(user)
    return user


@router.delete("/eliminar", include_in_schema=False)
@limiter.limit("3/minute")
def eliminar(request: Request, response: Response, data: EliminarCuentaRequest, db: Session = Depends(get_master_db), current_user: dict = Depends(get_current_user_from_token)):
    """Elimina de forma permanente la cuenta del usuario autenticado. Lo relacionado en master se borra en cascada."""
    user = db.query(User).filter(User.id == int(current_user.get("sub"))).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    if not verify_password(data.clave, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Clave incorrecta")

    # No dejar empresas sin ningún control activo
    otros = aliased(UserTenant)
    otro_control = db.query(otros.id).filter(
        otros.tenant_id == UserTenant.tenant_id,
        otros.usuario_id != user.id,
        otros.activo == True,
        otros.control == True,
    ).exists()
    empresas_sin_control = db.query(Tenant.nombre).join(UserTenant, UserTenant.tenant_id == Tenant.id).filter(
        UserTenant.usuario_id == user.id,
        UserTenant.activo == True,
        UserTenant.control == True,
        ~otro_control,
    ).all()
    if empresas_sin_control:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Eres el único control de estas empresas; asigna otro control antes de eliminar tu cuenta",
                "empresas": [e.nombre for e in empresas_sin_control],
            },
        )

    # Borrado directo en la base para que actúen los ON DELETE CASCADE
    db.query(User).filter(User.id == user.id).delete(synchronize_session=False)
    db.commit()
    logger.info(f"Cuenta eliminada por el propio usuario: id={user.id}")

    response.delete_cookie(key="access_token", httponly=True, secure=True, samesite="none")
    response.delete_cookie(key="refresh_token", httponly=True, secure=True, samesite="none", path="/")
    return {"detail": "Cuenta eliminada correctamente"}
