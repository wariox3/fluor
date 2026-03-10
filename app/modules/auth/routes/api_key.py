from app.core.rate_limit import limiter
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.security import require_admin
from app.modules.auth.schemas import ApiKeyCreate
from app.core.master_database import get_master_db
from app.core.security import generate_api_key, hash_api_key

from app.modules.auth.models import ApiKey

router = APIRouter()

@router.post("/api-key")
@limiter.limit("5/minute")
def nuevo(request: Request, data: ApiKeyCreate, db: Session = Depends(get_master_db), _: dict = Depends(require_admin)):
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