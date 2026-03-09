from fastapi.security import APIKeyHeader
from app.modules.auth.models import ApiKey
from app.core.master_database import get_master_db
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import secrets

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
    
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    return payload   

'''def require_admin(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos"
        )
    return user '''

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

def get_api_key(api_key: str = Depends(api_key_header), db: Session = Depends(get_master_db)):

    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API Key requerida"
        )

    try:
        prefix = api_key.split(".")[0]
    except:
        raise HTTPException(
            status_code=401,
            detail="API Key inválida"
        )

    key = db.query(ApiKey).filter(
        ApiKey.prefix == prefix,
        ApiKey.is_active == True
    ).first()

    if not key:
        raise HTTPException(
            status_code=401,
            detail="API Key inválida"
        )

    if not verify_api_key(api_key, key.key_hash):
        raise HTTPException(
            status_code=401,
            detail="API Key inválida"
        )

    return key