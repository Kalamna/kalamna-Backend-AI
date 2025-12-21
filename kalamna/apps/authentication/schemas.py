from typing import Literal

from pydantic import BaseModel, EmailStr

from kalamna.apps.business.schemas import BusinessCreateSchema
from kalamna.apps.employees.schemas import OwnerCreateSchema


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


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class LoginResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    role: str


class MeResponseSchema(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    business: str
