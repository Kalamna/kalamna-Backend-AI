"""
Authentication database models
Businesses model with id, email, and hashed_password fields
"""

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import String, Text, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from kalamna.db.base import Base


class IndustryEnum(Enum):
    TECHNOLOGY = "Technology"
    FINANCE = "Finance"
    HEALTHCARE = "Healthcare"
    EDUCATION = "Education"
    RETAIL = "Retail"
    MANUFACTURING = "Manufacturing"
    HOSPITALITY = "Hospitality"
    TRANSPORTATION = "Transportation"
    REAL_ESTATE = "Real Estate"
    ENTERTAINMENT = "Entertainment"
    OTHER = "Other"


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    industry: Mapped[IndustryEnum | None] = mapped_column(
        SAEnum(
            IndustryEnum,
            name="industry_enum",  # important!
            native_enum=True,
            validate_strings=True,
        ),
        nullable=True,
    )

    domain_url: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Business id={self.id} email={self.email!r}>"
