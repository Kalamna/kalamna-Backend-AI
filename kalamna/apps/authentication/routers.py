from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from kalamna.core.db import get_db

from kalamna.apps.authentication.schemas import RegisterSchema, GetMeSchema
from kalamna.apps.authentication.services import register_business_and_owner, get_current_user, permission_flag
from kalamna.apps.employees.models import Employee

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
    emp_data = GetMeSchema.model_validate(current_employee)
    emp_data.permission_flag = permission_flag(current_employee)
    
    return emp_data
