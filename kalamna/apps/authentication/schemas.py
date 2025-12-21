from typing import Literal

from pydantic import BaseModel, EmailStr

from kalamna.apps.business.schemas import BusinessCreateSchema
from kalamna.apps.employees.schemas import OwnerCreateSchema


# Base / Shared Schemas

class BaseTokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


# Auth  Schema
class RefreshTokenRequest(BaseModel):
    """
    Used by /auth/refresh
    MUST keep this name (already used elsewhere)
    """
    refresh_token: str


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class LoginResponseSchema(BaseTokenResponse):
    """
    Login returns BOTH tokens
    """
    refresh_token: str
    role: str


class RefreshResponseSchema(BaseTokenResponse):
    """
    Refresh returns ONLY new access token
    """
    pass

class RegisterSchema(BaseModel):
    business: BusinessCreateSchema
    owner: OwnerCreateSchema


# employee Info Schema

class MeResponseSchema(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    business: str
