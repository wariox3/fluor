from fastapi import APIRouter, HTTPException, status, Depends, Response
from sqlalchemy.orm import Session
from app.core.security import verify_password, create_access_token
from app.modules.auth.schemas import LoginRequest, LoginResponse, TokenResponse
from app.core.master_database import get_master_db

from app.modules.auth.models import User
from app.modules.auth.schemas import UserCreate, UserResponse
from app.core.security import hash_password, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=LoginResponse, response_model_exclude_none=True)
def login(data: LoginRequest, response: Response, db: Session = Depends(get_master_db)):
    
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    token_data = {
        "sub": str(user.id),
        "empresa_id": user.empresa_id,
        "role": user.role
    }

    access_token = create_access_token(token_data)

    user_data = {
        "id": user.id,
        "email": user.email,
        "empresa_id": user.empresa_id,
        "role": user.role
    }

    # modo web
    if data.client_type == "web":
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=3600
        )
        return {
            "user": user_data
        }

    # modo api / integraciones
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }


@router.post("/register", response_model=UserResponse)
def create_user(data: UserCreate, db: Session = Depends(get_master_db)):
    existing_user = db.query(User).filter(
        (User.email == data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario o email ya existe"
        )
    print(len(data.password))
    new_user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        empresa_id=data.empresa_id,
        role=data.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user