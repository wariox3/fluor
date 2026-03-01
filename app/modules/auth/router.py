from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.core.security import verify_password, create_access_token
from app.modules.auth.schemas import LoginRequest, TokenResponse
from app.core.database import get_db
from app.modules.auth.models import User
from app.modules.auth.schemas import UserCreate, UserResponse
from app.core.security import hash_password, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.username == data.username).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuario inactivo")

    token_data = {
        "sub": str(user.id),
        "empresa_id": user.empresa_id,
        "role": user.role
    }

    access_token = create_access_token(token_data)

    return {"access_token": access_token}

@router.post("/register", response_model=UserResponse)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Solo admin puede crear usuarios
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado"
        )

    # Validar duplicados
    existing_user = db.query(User).filter(
        (User.username == data.username) |
        (User.email == data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario o email ya existe"
        )

    new_user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        empresa_id=current_user["empresa_id"],  # multitenant automático
        role=data.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user