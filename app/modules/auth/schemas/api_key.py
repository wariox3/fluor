from pydantic import BaseModel, EmailStr
from typing import Literal, Optional

from app.modules.auth.models import UserRole
         
class ApiKeyCreate(BaseModel):
    name: str
    tenant_id: int   

class ApiKeyResponse(BaseModel):
    id: int
    name: str
    tenant_id: int | None = None
    prefix: str

    class Config:
        from_attributes = True          