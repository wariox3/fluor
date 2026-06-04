import logging
from app.core.rate_limit import limiter
from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session, sessionmaker
from app.core.security import require_admin, get_current_user
from app.core.master_database import get_master_db
from app.modules.auth.models.user import User, UserRole
from app.modules.auth.models.tenant import Tenant
from app.modules.auth.schemas.user import UserCreate, UserResponse, RegisterRequest, RegisterResponse, RecuperarClaveRequest, RestablecerClaveRequest, AsociarRequest, ReenviarVerificacionRequest, ActualizarPerfilRequest, PerfilResponse
from app.core.security import hash_password, generate_verification_token
from app.core.config import APP_URL
from app.core.zinc import Zinc
from app.core.turnstile import verify_turnstile
from app.core.tenant_database import get_tenant_engine
from app.modules.rhu.models.empleado import Empleado
from typing import List
from app.modules.auth.schemas.user import UserListResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/detalle", response_model=PerfilResponse, include_in_schema=False)
def detalle(db: Session = Depends(get_master_db), current_user: dict = Depends(get_current_user)):
    user = db.query(User).filter(User.id == int(current_user.get("sub"))).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user


@router.post("/nuevo", response_model=UserResponse, include_in_schema=False)
@limiter.limit("5/minute")
def nuevo(request: Request, data: UserCreate, db: Session = Depends(get_master_db), _: dict = Depends(require_admin)):
    existing_user = db.query(User).filter((User.email == data.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario o email ya existe"
        )

    new_user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        tenant_id=data.tenant_id,
        role=data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/registrar", response_model=RegisterResponse, include_in_schema=False)
@limiter.limit("3/minute")
def registrar(request: Request, data: RegisterRequest, db: Session = Depends(get_master_db)):
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
        verification_token=token,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    verification_link = f"{APP_URL}/auth/verify-email?token={token}"

    html_content = f"""
        <h1>¡Hola {new_user.nombres}!</h1>
        <p>Estamos comprometidos con la seguridad. Por favor verifica tu cuenta haciendo clic en el siguiente enlace.</p>
        <a href='{verification_link}'>Verificar cuenta</a>
    """
    try:
        Zinc().correo(new_user.email, "Verifica tu cuenta", html_content)
    except Exception as e:
        logger.warning(f"No se pudo enviar correo de verificación a {new_user.email}: {e}")

    return RegisterResponse(user=UserResponse.model_validate(new_user), verification_link=verification_link)


@router.post("/recuperar-clave", include_in_schema=False)
@limiter.limit("3/minute")
def recuperar_clave(request: Request, data: RecuperarClaveRequest, db: Session = Depends(get_master_db)):
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
        user.reset_password_token = token
        db.commit()
        reset_link = f"{APP_URL}/auth/restablecer-clave?token={token}"
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
def restablecer_clave(request: Request, data: RestablecerClaveRequest, db: Session = Depends(get_master_db)):
    verify_turnstile(data.turnstile_token)

    user = db.query(User).filter(User.reset_password_token == data.token).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido o expirado")
    user.password_hash = hash_password(data.nueva_clave)
    user.reset_password_token = None
    db.commit()
    return {"detail": "Clave restablecida correctamente"}


@router.get("/verificar", include_in_schema=False)
@limiter.limit("10/minute")
def verificar(request: Request, token: str, db: Session = Depends(get_master_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido")
    if user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cuenta ya verificada")
    user.is_verified = True
    user.verification_token = None
    db.commit()
    return {"detail": "Cuenta verificada correctamente"}

@router.post("/reenviar-verificacion", include_in_schema=False)
@limiter.limit("3/minute")
def reenviar_verificacion(request: Request, data: ReenviarVerificacionRequest, db: Session = Depends(get_master_db)):
    verify_turnstile(data.turnstile_token)

    user = db.query(User).filter(User.email == data.email).first()
    if user and not user.is_verified:
        token = generate_verification_token()
        user.verification_token = token
        db.commit()
        verification_link = f"{APP_URL}/auth/verify-email?token={token}"
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


@router.post("/asociar", include_in_schema=False)
@limiter.limit("10/minute")
def asociar(request: Request, data: AsociarRequest, db: Session = Depends(get_master_db), current_user: dict = Depends(get_current_user),):
    if int(current_user.get("sub")) != data.usuario_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Estas tratando de cambiar informacion de otro usuario")

    user = db.query(User).filter(User.id == data.usuario_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario no encontrado")
    if user.tenant_id == data.tenant_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya está asociado a esta empresa")
    if user.role != UserRole.employee:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solo los usuarios con rol empleado pueden ser asociados a una empresa")
    tenant = db.query(Tenant).filter(Tenant.id == data.tenant_id).first()
    if not tenant or not tenant.schema:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empresa no encontrada")

    engine = get_tenant_engine(tenant.schema)
    TenantSession = sessionmaker(bind=engine)
    tenant_db = TenantSession()
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
            detail=f"No se encontró un empleado con ese número de identificación {user.numero_identificacion} y correo {user.email} en la empresa indicada"
        )

    user.tenant_id = data.tenant_id
    user.empleado_id = empleado.codigo_empleado_pk
    db.commit()
    return {"detail": "Usuario asociado correctamente a la empresa"}


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

@router.get("/lista", response_model=List[UserListResponse], include_in_schema=False)
def lista(
    db: Session = Depends(get_master_db),
    current_user: dict = Depends(require_admin)
):
    """
    Lista todos los usuarios. Solo accesible para administradores.
    """
    users = db.query(User).order_by(User.id.asc()).all()
    return users