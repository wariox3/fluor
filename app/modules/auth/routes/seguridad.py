from app.core.rate_limit import limiter
from fastapi import APIRouter, HTTPException, status, Depends, Response, Request
from sqlalchemy.orm import Session
from app.core.security import verify_password, create_access_token
from app.modules.auth.schemas import LoginRequest, LoginResponse
from app.core.master_database import get_master_db

from app.modules.auth.models import User

router = APIRouter()

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
