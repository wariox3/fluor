from app.core.rate_limit import limiter
from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from app.core.security import require_admin
from app.core.master_database import get_master_db
from app.modules.auth.models.user import User, UserRole
from app.modules.auth.schemas.user import UserCreate, UserResponse, RegisterRequest, RegisterResponse
from app.core.security import hash_password, generate_verification_token
from app.core.config import APP_URL

router = APIRouter()

@router.post("/nuevo", response_model=UserResponse)
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


@router.post("/registrar", response_model=RegisterResponse)
@limiter.limit("3/minute")
def registrar(request: Request, data: RegisterRequest, db: Session = Depends(get_master_db)):
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
    # TODO: enviar verification_link por correo a new_user.email

    return RegisterResponse(user=UserResponse.model_validate(new_user), verification_link=verification_link)


@router.get("/verificar")
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
