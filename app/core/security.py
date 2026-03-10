from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from app.modules.auth.models import ApiKey
from app.core.master_database import get_master_db
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
import secrets

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_refresh_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token no es un refresh token",
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado",
        )

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
    
def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    bearer: HTTPAuthorizationCredentials = Security(bearer_scheme),
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_master_db),
) -> dict:
    # 1. OAuth2 / JWT
    if token:
        return decode_token(token)

    # 2. Bearer directo
    if bearer:
        return decode_token(bearer.credentials)

    # 3. API Key (requiere DB)
    if api_key:
        try:
            prefix = api_key.split(".")[0]
        except Exception:
            raise HTTPException(status_code=401, detail="API Key inválida")
        key = db.query(ApiKey).filter(ApiKey.prefix == prefix, ApiKey.is_active == True).first()

        if not key or not verify_api_key(api_key, key.key_hash):
            raise HTTPException(status_code=401, detail="API Key inválida")

        if key.expires_at and key.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="API Key expirada")

        key.last_used_at = datetime.now(timezone.utc)
        db.commit()

        return {
            "sub": key.prefix,
            "tenant_id": key.tenant_id,
            "tenant_schema": key.tenant.schema if key.tenant else None,
        }

    # 4. Cookie / Session
    session_token = request.cookies.get("access_token")
    if session_token:
        return decode_token(session_token)

    raise HTTPException(
        status_code=401,
        detail="No autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_current_user_from_token(request: Request, token: str = Depends(oauth2_scheme), bearer: HTTPAuthorizationCredentials = Security(bearer_scheme),) -> dict:
    """Autenticación solo por JWT/Bearer/Cookie — sin conexión a DB."""
    if token:
        return decode_token(token)
    if bearer:
        return decode_token(bearer.credentials)
    session_token = request.cookies.get("access_token")
    if session_token:
        return decode_token(session_token)
    raise HTTPException(
        status_code=401,
        detail="No autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )

def require_admin(user: dict = Depends(get_current_user_from_token)):
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador"
        )
    return user

def require_admin_control(user: dict = Depends(get_current_user_from_token)):
    if user.get("role") != "admin" and user.get("role") != "control":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador o control"
        )
    return user

def generate_api_key():
    raw_prefix = secrets.token_hex(4)
    prefix = f"erp_{raw_prefix}"    
    secret = secrets.token_urlsafe(32)
    api_key = f"{prefix}.{secret}"
    return prefix, api_key

def hash_api_key(key: str):
    return pwd_context.hash(key)

def verify_api_key(key: str, hashed: str):
    return pwd_context.verify(key, hashed)
