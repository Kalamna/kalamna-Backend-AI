from typing import Optional
from uuid import UUID
from pydantic import BaseModel, field_validator
from datetime import datetime

class GetMeSchema(BaseModel):
    id: UUID
    full_name: str
    email: str
    business_id: UUID
    role: str
    permission_flag: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    @field_validator("permission_flag")
    def compute_permission_flag(cls, v, values):
        role= values["role", ""]
        return "owner" if role == "OWNER" else "staff"

    class Config:
        from_attributes = True
        extra = "allow"

class LoginSchema(BaseModel):
    email: str
    password: str
    class Config:
        from_attributes = True

class RefreshTokenSchema(BaseModel):
    token: str