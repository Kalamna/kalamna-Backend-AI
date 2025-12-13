"""
Employee Pydantic schemas
Request/response schemas for employee CRUD and permission management
"""

from pydantic import BaseModel, EmailStr, Field


# owner registration schema
class OwnerCreateSchema(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
