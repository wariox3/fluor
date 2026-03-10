from typing import List
from app.core.rate_limit import limiter
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.security import require_admin_control
from app.modules.auth.schemas.api_key import ApiKeyCreate, ApiKeyResponse
from app.core.master_database import get_master_db
from app.core.security import generate_api_key, hash_api_key
from app.modules.auth.models import ApiKey

router = APIRouter()

@router.post("/nuevo")
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

@router.get("/lista", response_model=List[ApiKeyResponse])
def lista(page: int = 1, size: int = 50, db: Session = Depends(get_master_db)):
    offset = (page - 1) * size
    api_keys = (
        db.query(ApiKey)
        .offset(offset)
        .limit(size)
        .all()
    )

    return api_keys