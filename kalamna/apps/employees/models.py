"""
Employee database models
Employee model with name, role, email , password, and business_id ,is_verifed, is_active, created_at, updated_at
"""

from kalamna.db.base import Base
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid


class EmployeeRole(Enum):
    OWNER = "owner"
    STAFF = "staff"


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id"),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    role: Mapped[EmployeeRole] = mapped_column(
        SAEnum(EmployeeRole, name="employee_role_enum", native_enum=True),
        nullable=False,
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
    # TODO:
    """
    Integrate the invitation system into the Employee model.

    - Add `invitation_id` as a foreign key to link each employee to the
      specific invitation they were created from.
    - Later in the auth logic, use `is_verified`
      to restrict access to login until the employee has confirm
      their invitation.
    """

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    email_verified_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    )

# relationship
    business = relationship(
        "Business", back_populates="employees"
    )  # MANY employees → ONE business

    def __repr__(self) -> str:
        return f"<Employee id={self.id} email={self.email!r}>"
