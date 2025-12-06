from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from kalamna.core.db import get_db

from kalamna.apps.authentication.schemas import RegisterSchema, GetMeSchema, LoginSchema
from kalamna.apps.authentication.services import register_business_and_owner, get_current_user, RefreshTokenRequest, login_validation
from kalamna.apps.employees.models import Employee

from kalamna.core.security import create_access_token, create_refresh_token, decode_token
from kalamna.core.security import ACCESS_TTL
from datetime import datetime, timezone

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new business and its owner employee",
)
async def register(
    data: RegisterSchema,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    """
    Create a new business + owner employee account in a single request.
    After success, owner must verify their email to activate the account.
    """
    try:
        await register_business_and_owner(data, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    return {
        "message": "Account created successfully. Please check your email to verify your account."
        # TODO: In the future, add a boolean to indicate if verification email was sent
    }

@router.get("/me", response_model=GetMeSchema)
async def get(current_employee: Employee = Depends(get_current_user)):
    # add permission flag dynamically
    emp_data = GetMeSchema.from_orm(current_employee)
    emp_data.permission_flag = "owner" if current_employee.role == "OWNER" else "staff"

    return emp_data


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Login to get access and refresh tokens",
)
async def login(data: LoginSchema, db: AsyncSession = Depends(get_db)):
    employee, business = await login_validation(data, db)
    
    # Generate tokens using existing JWT builder
    access_token = create_access_token(
        employee_id=str(employee.id),
        role=str(employee.role)
    )
    refresh_token = create_refresh_token(employee_id=str(employee.id))
    now = datetime.now(timezone.utc)
    return {
        "access": access_token,
        "refresh": refresh_token,
        "message": "login success",
        "token expire time": now + ACCESS_TTL
    }

@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
)
async def refresh_token(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
        payload = decode_token(data.refresh_token, audience="refresh")
        employee_id = payload["sub"]
        employee_record = await db.execute(select(Employee).where(Employee.id == employee_id))
        employee = employee_record.scalars().first()
        role = employee.role
        access = create_access_token(
            employee_id=str(employee.id),
            role=str(employee.role)
        )
        refresh = create_refresh_token(employee_id=str(employee.id))
        now = datetime.now(timezone.utc)
        return {
            "access token": access,
            "refresh token": refresh,
            "expire time": now + ACCESS_TTL,
        }
