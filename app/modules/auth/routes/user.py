from app.core.rate_limit import limiter
from fastapi import APIRouter, HTTPException, status, Depends, Response, Request
from sqlalchemy.orm import Session
from app.core.security import require_admin
from app.core.master_database import get_master_db
from app.modules.auth.models.user import User, UserRole
from app.modules.auth.schemas.user import UserCreate, UserResponse, RegisterRequest
from app.core.security import hash_password

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


@router.post("/registrar", response_model=UserResponse)
@limiter.limit("3/minute")
def registrar(request: Request, data: RegisterRequest, db: Session = Depends(get_master_db)):
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya está registrado"
        )
    new_user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        nombres=data.nombres,
        apellidos=data.apellidos,
        numero_identificacion=data.numero_identificacion,
        role=UserRole.employee
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
