from app.core.rate_limit import limiter
from fastapi import APIRouter, HTTPException, status, Depends, Response, Request
from sqlalchemy.orm import Session
from app.core.security import require_admin, verify_password, create_access_token
from app.modules.auth.schemas import ApiKeyCreate, LoginRequest, LoginResponse, TokenResponse
from app.core.master_database import get_master_db
from app.core.security import generate_api_key, hash_api_key

from app.modules.auth.models import Tenant, User, ApiKey
from app.modules.auth.schemas import UserCreate, UserResponse
from app.core.security import hash_password, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=LoginResponse, response_model_exclude_none=True)
@limiter.limit("5/minute")
def login(request: Request, data: LoginRequest, response: Response, db: Session = Depends(get_master_db)):    
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    token_data = {
        "sub": str(user.id),
        "tenant_id": user.tenant_id,
        "tenant_schema": user.tenant.schema if user.tenant else None,
        "role": user.role
    }

    access_token = create_access_token(token_data)

    user_data = {
        "id": user.id,
        "email": user.email,
        "tenant_id": user.tenant_id,
        "tenant_schema": user.tenant.schema if user.tenant else None,
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

@router.post("/logout")
def logout(request: Request, response: Response):
    if request.cookies.get("access_token"):
        response.delete_cookie(
            key="access_token",
            httponly=True,
            secure=True,
            samesite="lax"
        )
        return {"message": "Sesión cerrada"}
    return {"message": "Sesión cerrada"}

@router.post("/register", response_model=UserResponse)
@limiter.limit("5/minute")
def create_user(data: UserCreate, db: Session = Depends(get_master_db), _: dict = Depends(require_admin)):
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

@router.post("/api-key")
@limiter.limit("5/minute")
def create_api_key(data: ApiKeyCreate, db: Session = Depends(get_master_db), _: dict = Depends(require_admin)):
    prefix, api_key = generate_api_key()
    key = ApiKey(
        name=data.name,
        tenant_id=data.tenant_id,
        prefix=prefix,
        key_hash=hash_api_key(api_key)
    )

    db.add(key)
    db.commit()
    
    return {
        "api_key": api_key,
        "prefix": prefix,
        "warning": "Guarda esta API Key, no podrá ser recuperada después"
    }