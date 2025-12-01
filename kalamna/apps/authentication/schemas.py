"""
Organization Pydantic schemas
Request/response schemas for organization CRUD operations
"""
from typing import Literal
from pydantic import BaseModel

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str