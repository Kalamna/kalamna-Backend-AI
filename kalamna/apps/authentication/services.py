"""
Auth logic for registering a new business and its owner & logging in
"""
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from kalamna.apps.business.models import Business
from kalamna.apps.employees.models import Employee, EmployeeRole
from kalamna.core.security import hash_password
from kalamna.apps.authentication.schemas import RegisterSchema


async def register_business_and_owner(data: RegisterSchema, db: AsyncSession):
    """
    Register a new business and its owner employee
    in one endpoint
    """
    b = data.business
    o = data.owner

    # check business email
    existing_business = await db.scalar(
        select(Business).where(Business.email == b.email)
    )
    if existing_business:
        # if exists, return message
        raise ValueError("Business email already exists")

    # check employee email
    existing_employee = await db.scalar(
        select(Employee).where(Employee.email == o.email)
    )
    if existing_employee:
        # if exists, return message
        raise ValueError("Employee email already exists")

    # Create Business
    business = Business(
        name=b.name,
        email=b.email,
        industry=b.industry,
        description=b.description,
        domain_url=b.domain_url
    )
    db.add(business)
    await db.flush()   # get business.id

    # Hash password
    hashed = await asyncio.to_thread(hash_password, o.password)

    # Create Employee with role=OWNER
    owner = Employee(
        full_name=o.full_name,
        email=o.email,
        password=hashed,
        business_id=business.id,
        role=EmployeeRole.OWNER,
        is_verified=False,
        is_active=False,
        email_verified_at=None
    )
    db.add(owner)

    # Commit to db
    await db.commit()

    return business, owner

