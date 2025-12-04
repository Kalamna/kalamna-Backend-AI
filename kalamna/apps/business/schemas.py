from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

class GetMeSchema(BaseModel):
    full_name: str
    email: str
    business_id: UUID
    role: str
    permission_flag: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    # @field_validator("permission_flag", mode="before")
    # def compute_permission_flag( cls, v, values ):
    #     role = values["role", ""]
    #     return "owner" if role == "owner" else "staff"

    class Config:
        from_attributes = True