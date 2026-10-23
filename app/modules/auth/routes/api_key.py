from app.core.rate_limit import limiter
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from app.core.security import get_current_user_from_token, require_admin_control
from app.modules.auth.schemas.api_key import ApiKeyCreate, ApiKeyResponse
from app.core.master_database import get_master_db
from app.core.security import generate_api_key, hash_api_key
from app.modules.auth.models.api_key import ApiKey
from app.modules.mas.models.user_tenant import es_control

router = APIRouter()

@router.post("/nuevo", include_in_schema=False)
@limiter.limit("5/minute")
def nuevo(request: Request, response: Response, data: ApiKeyCreate, db: Session = Depends(get_master_db), current_user: dict = Depends(require_admin_control)):
    prefix, api_key = generate_api_key()
    key = ApiKey(
        name=data.name,
        tenant_id=data.tenant_id,
        usuario_id=int(current_user["sub"]),
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

@router.get("/lista", response_model=list[ApiKeyResponse], include_in_schema=False)
def lista(tenant_id: int, page: int = 1, size: int = 50, db: Session = Depends(get_master_db), current_user: dict = Depends(get_current_user_from_token)):
    """API keys de una empresa. Solo para quien es control activo en ella."""
    if not es_control(db, int(current_user["sub"]), tenant_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para ver las API keys de esta empresa")

    offset = (page - 1) * size
    api_keys = (
        db.query(ApiKey)
        .filter(ApiKey.tenant_id == tenant_id)
        .order_by(ApiKey.id)
        .offset(offset)
        .limit(size)
        .all()
    )
    return api_keys

@router.delete("/eliminar/{api_key_id}", include_in_schema=False)
@limiter.limit("5/minute")
def eliminar(request: Request, response: Response, api_key_id: int, db: Session = Depends(get_master_db), _: dict = Depends(require_admin_control)):
    key = db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API Key no encontrada")

    db.delete(key)
    db.commit()
    return {"message": "API Key eliminada correctamente"}