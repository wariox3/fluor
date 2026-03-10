from pydantic import BaseModel
from datetime import datetime
from app.modules.auth.models import ApiKey         
class ApiKeyCreate(BaseModel):
    name: str
    tenant_id: int   

class ApiKeyResponse(BaseModel):
    id: int
    name: str
    tenant_id: int | None = None
    prefix: str
    created_at: datetime
    expires_at: datetime | None = None
    last_used_at: datetime | None = None

    class Config:
        from_attributes = True          