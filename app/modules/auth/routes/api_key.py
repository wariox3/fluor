from typing import List, Optional
from app.core.rate_limit import limiter
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.security import require_admin_control
from app.modules.auth.schemas.api_key import ApiKeyCreate, ApiKeyResponse
from app.core.master_database import get_master_db
from app.core.security import generate_api_key, hash_api_key
from app.modules.auth.models.api_key import ApiKey

router = APIRouter()

@router.post("/nuevo", include_in_schema=False)
@limiter.limit("5/minute")
def nuevo(request: Request, data: ApiKeyCreate, db: Session = Depends(get_master_db), _: dict = Depends(require_admin_control)):
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

@router.get("/lista", response_model=List[ApiKeyResponse], include_in_schema=False)
def lista(page: int = 1, size: int = 50, tenant_id: Optional[str] = None, db: Session = Depends(get_master_db)):
    offset = (page - 1) * size
    query = db.query(ApiKey)    
    if tenant_id:
        query = query.filter(ApiKey.tenant_id == tenant_id)    
    api_keys = query.offset(offset).limit(size).all()
    return api_keys

@router.delete("/eliminar/{api_key_id}", include_in_schema=False)
@limiter.limit("5/minute")
def eliminar(request: Request, api_key_id: int, db: Session = Depends(get_master_db), _: dict = Depends(require_admin_control)):
    key = db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API Key no encontrada")

    db.delete(key)
    db.commit()
    return {"message": "API Key eliminada correctamente"}