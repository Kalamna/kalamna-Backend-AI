from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from kalamna.core.db import get_db
from kalamna.apps.authentication.schemas import RegisterSchema
from kalamna.apps.authentication.services.register_service import (
    register_business_and_owner
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new business and its owner employee",
)
async def register(
        data: RegisterSchema,
        db: AsyncSession = Depends(get_db)
):
    """
    Create a new business + owner employee account in a single request.
    After success , owner must verify their email to activate the account.
    """
    try:
        await register_business_and_owner(data, db)
    except ValueError as e:
        # validation error (email duplicate, password invalid, etc.)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return {
        "message": "Account created successfully. Please check your email to verify your account."
        #TODO : in future , add boolen if verifaction email sent or not
    }
