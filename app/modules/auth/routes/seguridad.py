from app.core.rate_limit import limiter
from fastapi import APIRouter, HTTPException, status, Depends, Response, Request
from sqlalchemy.orm import Session
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_refresh_token, get_current_user_from_token
from app.core.turnstile import verify_turnstile
from app.modules.auth.schemas.user import LoginRequest, LoginResponse, UserInfo
from sqlalchemy.orm import joinedload
from app.core.master_database import get_master_db
from app.modules.auth.models.user import User

router = APIRouter()

@router.post("/login", response_model=LoginResponse, response_model_exclude_none=True, include_in_schema=False)
@limiter.limit("5/minute")
def login(request: Request, data: LoginRequest, response: Response, db: Session = Depends(get_master_db)):    
    if data.client_type not in ("integration", "api"):
        verify_turnstile(data.turnstile_token)

    user = db.query(User).options(joinedload(User.tenant)).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Cuenta no verificada", "is_verified": False}
        )

    token_data = {
        "sub": str(user.id),
        "tenant_id": user.tenant_id,
        "role": user.role,
        "empleado_id": user.empleado_id
    }

    access_token = create_access_token(token_data)

    user_data = {
        "id": user.id,
        "email": user.email,
        "tenant_id": user.tenant_id,
        "tenant_nombre": user.tenant.nombre if user.tenant else None,
        "role": user.role,
        "empleado_id": user.empleado_id
    }

    # modo web
    if data.client_type == "web":
        refresh_token = create_refresh_token(token_data)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=3600
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="none",
            path="/",
            max_age=7 * 24 * 3600
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

@router.post("/refresh", include_in_schema=False)
@limiter.limit("10/minute")
def refresh(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token no encontrado"
        )

    payload = decode_refresh_token(token)

    token_data = {
        "sub": payload["sub"],
        "tenant_id": payload.get("tenant_id"),
        "role": payload.get("role"),
    }

    new_access_token = create_access_token(token_data)
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=3600
    )
    return {"message": "Token renovado"}

@router.post("/logout", include_in_schema=False)
def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="none",
    )
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
    )
    return {"message": "Sesión cerrada"}

@router.get("/me", response_model=UserInfo, include_in_schema=False)
def me(current_user: dict = Depends(get_current_user_from_token), db: Session = Depends(get_master_db)):
    user = db.query(User).options(joinedload(User.tenant)).filter(User.id == int(current_user["sub"])).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return UserInfo(
        id=user.id,
        email=user.email,
        tenant_id=user.tenant_id,
        tenant_nombre=user.tenant.nombre if user.tenant else None,
        role=user.role,
        empleado_id=user.empleado_id
    )

