"""
Auth logic for registering a new business and its owner employee
"""

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from kalamna.apps.business.models import Business
from kalamna.apps.employees.models import Employee, EmployeeRole
from kalamna.core.security import hash_password
from kalamna.apps.authentication.schemas import RegisterSchema, LoginSchema, RefreshTokenRequest
from kalamna.core.validation import validate_password, ValidationError

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status

from kalamna.core.security import decode_token
from kalamna.core.db import get_db

async def register_business_and_owner(data: RegisterSchema, db: AsyncSession):
    """
    Register a new business and its owner employee in one endpoint.
    """

    b = data.business
    o = data.owner

    # Check business email
    existing_business = await db.scalar(
        select(Business).where(Business.email == b.email)
    )
    if existing_business:
        raise ValueError("Business email already exists")

    # Check employee email
    existing_employee = await db.scalar(
        select(Employee).where(Employee.email == o.email)
    )
    if existing_employee:
        raise ValueError("Employee email already exists")

    # Create Business
    business = Business(
        name=b.name,
        email=b.email,
        industry=b.industry,
        description=b.description,
        domain_url=str(b.domain_url) if b.domain_url else None,
    )

    db.add(business)
    await db.flush()  # get business.id

    # Validate password
    try:
        validate_password(o.password)
    except ValidationError as e:
        raise ValueError(str(e)) from e

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
        email_verified_at=None,
    )
    db.add(owner)

    await db.commit()

    return business, owner

security = HTTPBearer()

async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_token(token, audience="access")
    employee_id = payload['sub']
    query = await db.execute(select(Employee).where(Employee.id==employee_id))
    employee = query.scalar_one_or_none()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


async def login_validation(data: LoginSchema, db: AsyncSession = Depends(get_db)):
    """
    Validate login credentials and return employee object
    """
    # fetch the employee from database:
    employees_records = await db.execute( select(Employee).where(Employee.email == data.email) )
    employee = employees_records.scalars().first()
    # validate email
    if employee == None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='invalid email or password'
        )
    # validate password
    if data.password!=employee.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='invalid email or password'
        )
    # Check employee + business verification
    if not employee.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='your email is not verified please check your inbox'
        )
    if not employee.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='your email is not verified please check your inbox'
        )
    business_record = await db.execute(select(Business).where(Business.id == employee.business_id))
    business = business_record.scalars().first()
    return employee, business