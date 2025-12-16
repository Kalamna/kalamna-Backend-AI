from typing import Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl

from kalamna.apps.business.models import IndustryEnum


# businesses registration schema
class BusinessCreateSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    industry: IndustryEnum
    description: Optional[str] = None
    domain_url: Optional[HttpUrl] = None
