from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from kalamna.apps.employees.models import Employee
from kalamna.core.db import get_db
from kalamna.core.security import decode_token

# bearer-only scheme
bearer_scheme = HTTPBearer()


async def get_current_employee(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Employee:
    token = credentials.credentials
    try:
        payload = decode_token(token, audience="access")
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from err

    employee_id = payload.get("sub")

    stmt = (
        select(Employee)
        # eager load business to avoid async lazy-load during access
        .options(selectinload(Employee.business))
        .where(Employee.id == employee_id)
    )
    result = await db.execute(stmt)
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return employee
