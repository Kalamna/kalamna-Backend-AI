from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from kalamna.apps.authentication.dependencies import get_current_employee
from kalamna.apps.authentication.schemas import (
    LoginResponseSchema,
    LoginSchema,
    MeResponseSchema,
    RefreshResponseSchema,
    RefreshTokenRequest,
    RegisterSchema,
)
from kalamna.apps.authentication.services import (
    login,
    logout,
    refresh_access_token,
    register_business_and_owner,
)
from kalamna.apps.employees.models import Employee
from kalamna.core.db import get_db
from kalamna.utils.mailer import send_email

router = APIRouter(prefix="/auth", tags=["Authentication"])


# register new business + owner endpoint
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


@router.post("/test-email")
async def test_email(
    background_tasks: BackgroundTasks,
    email_to: EmailStr,
):
    """
    Test email sending functionality.
    """
    await send_email(
        background_tasks=background_tasks,
        subject="Test Email from Kalamna",
        email_to=[email_to],
        template_name="mail.html",
        context={"name": "Test User"},
    )
    return {"message": "Test email sent in the background."}


# login endpoint
@router.post(
    "/login",
    response_model=LoginResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Login an existing verified employee",
)
async def login_employee(
    data: LoginSchema,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate employee and issue access & refresh tokens.
    """
    try:
        result = await login(
            email=data.email,
            password=data.password,
            db=db,
        )

        return {
            "message": "Login successful",
            **result,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from e


# get current authenticated employee info endpoint
@router.get(
    "/me",
    response_model=MeResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated employee info",
)
async def get_me(
    current_employee: Employee = Depends(get_current_employee),
):
    return {
        "id": str(current_employee.id),
        "email": current_employee.email,
        "full_name": current_employee.full_name,
        "role": current_employee.role.value,
        "business": current_employee.business.name,
    }


# refresh token endpoint
@router.post(
    "/refresh",
    response_model=RefreshResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
)
async def refresh_token_endpoint(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await refresh_access_token(
            refresh_token=data.refresh_token,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from e


# logout endpoint
@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout and revoke refresh token",
)
async def logout_endpoint(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await logout(
            refresh_token=data.refresh_token,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from e
