"""
Auth logic for registering a new business and its owner employee
"""

import asyncio
from datetime import datetime, timezone

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from kalamna.apps.authentication.models import RefreshToken
from kalamna.apps.authentication.schemas import RegisterSchema
from kalamna.apps.business.models import Business
from kalamna.apps.employees.models import Employee, EmployeeRole
from kalamna.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from kalamna.core.validation import ValidationError, validate_password
from kalamna.utils.mailer import send_email


# register service
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


# send test email service
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


# login service
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
    employee = await db.scalar(select(Employee).where(Employee.email == email))

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


# refresh access token service
async def refresh_access_token(
    *,
    refresh_token: str,
    db: AsyncSession,
):
    """
    Validate refresh token and issue a new access token.
    """

    # Decode refresh JWT
    try:
        payload = decode_token(refresh_token, audience="refresh")
    except Exception as err:
        raise ValueError("Invalid or expired refresh token") from err

    jti = payload.get("jti")
    employee_id = payload.get("sub")

    if not jti or not employee_id:
        raise ValueError("Invalid or expired refresh token")

    # Lookup refresh token in DB
    token_row = await db.scalar(select(RefreshToken).where(RefreshToken.jti == jti))

    if not token_row:
        raise ValueError("Invalid or expired refresh token")

    # Check if revoked / expired
    now = datetime.now(timezone.utc)

    if token_row.revoked_at is not None:
        raise ValueError("Invalid or expired refresh token")

    if token_row.expires_at < now:
        raise ValueError("Invalid or expired refresh token")

    # Fetch employee and issue new access token
    employee = await db.get(Employee, employee_id)
    if not employee:
        raise ValueError("Invalid or expired refresh token")

    access_token = create_access_token(
        employee_id=str(employee.id),
        role=employee.role.value,
    )

    return {
        "access_token": access_token,
        "expires_in": 900,
        "token_type": "bearer",
    }


# logout service
async def logout(
    *,
    refresh_token: str,
    db: AsyncSession,
):
    """
    Revoke a refresh token (logout).
    """

    # Decode refresh token
    try:
        payload = decode_token(refresh_token, audience="refresh")
    except Exception as err:
        raise ValueError("Invalid or expired refresh token") from err

    jti = payload.get("jti")
    if not jti:
        raise ValueError("Invalid or expired refresh token")

    # check for refresh token in DB
    token_row = await db.scalar(select(RefreshToken).where(RefreshToken.jti == jti))

    if not token_row:
        raise ValueError("Invalid or expired refresh token")

    # check If already revoked ,  treat as invalid else revoke it
    if token_row.revoked_at is not None:
        raise ValueError("Invalid or expired refresh token")

    token_row.revoked_at = datetime.now(timezone.utc)
    await db.commit()

    return {"message": "Logged out successfully"}
