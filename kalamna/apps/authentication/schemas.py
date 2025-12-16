from typing import Literal

from pydantic import BaseModel

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
