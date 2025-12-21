"""
Auth logic for registering a new business and its owner employee
"""

import asyncio

from fastapi import BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from kalamna.apps.authentication.schemas import RegisterSchema
from kalamna.apps.business.models import Business
from kalamna.apps.employees.models import Employee, EmployeeRole
from kalamna.core.validation import ValidationError, validate_password
from kalamna.utils.mailer import send_email
from datetime import datetime, timezone
from kalamna.apps.authentication.models import RefreshToken
from fastapi import HTTPException, status
from kalamna.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
    hash_password,
)


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

    # Check domain URL
    if b.domain_url:
        existing_domain = await db.scalar(
            select(Business).where(Business.domain_url == str(b.domain_url))
        )
        if existing_domain:
            raise ValueError("Business domain already exists")

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


async def test_email(background_tasks: BackgroundTasks, email_to: list[str]):
    if not email_to:
        raise ValueError("Recipient email address(es) must be provided")
    await send_email(
        background_tasks=background_tasks,
        subject="Test Email from Kalamna",
        email_to=email_to,
        template_name="mail.html",
        context={},
    )
    return {"message": "Email queued for sending"}


async def login(
    *,
    email: str,
    password: str,
    db: AsyncSession,
):
    """
    Authenticate employee and issue access & refresh tokens.
    """

    # Fetch employee by email & verify password
    employee = await db.scalar(
        select(Employee).where(Employee.email == email)
    )

    if not employee or not verify_password(password, employee.password):
        raise ValueError("Invalid email or password")

    # check Account is active & verified
    if not employee.is_active or not employee.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not verified or has been disabled.",
        )

    # create tokens & decode refresh token using shared helper
    access_token = create_access_token(
        employee_id=str(employee.id),
        role=employee.role.value,
    )

    refresh_token = create_refresh_token(
        employee_id=str(employee.id),
    )

    payload = decode_token(refresh_token, audience="refresh")

    refresh_jti = payload["jti"]
    refresh_exp = datetime.fromtimestamp(
        payload["exp"],
        tz=timezone.utc,
    )
    # store refresh token in DB
    db.add(
        RefreshToken(
            jti=refresh_jti,
            employee_id=employee.id,
            expires_at=refresh_exp,
        )
    )

    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 900,
        "role": employee.role.value,
    }
