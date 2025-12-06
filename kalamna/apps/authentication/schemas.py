from typing import Literal
from pydantic import BaseModel
from kalamna.apps.business.schemas import BusinessCreateSchema
from kalamna.apps.employees.schemas import OwnerCreateSchema
from uuid import UUID
from datetime import datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RegisterSchema(BaseModel):
    business: BusinessCreateSchema
    owner: OwnerCreateSchema
    # maybe will add model config for swagger

class GetMeSchema(BaseModel):
    id: UUID
    full_name: str
    email: str
    business_id: UUID
    role: str
    permission_flag: str = "staff"
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        extra = "allow"

class LoginSchema(BaseModel):
    email: str
    password: str
    class Config:
        from_attributes = True


