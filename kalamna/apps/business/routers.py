"""
Authentication API routes
Endpoints: /login, /register, /refresh, /logout, /me
"""
from datetime import datetime, timezone
from fastapi import APIRouter,Depends, HTTPException, status
from .models import Business
from kalamna.apps.employees.models import Employee
from .schemas import GetMeSchema
from ...core import db
from kalamna.core.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

router = APIRouter(
    prefix='/business',
    tags=['Business']
)


def permission_flag(emp):
    pass


@router.get("/me", response_model=List[GetMeSchema])
async def get(db: AsyncSession = Depends(get_db)):
    # fetch all employees from database:
    employees_records = await db.execute( select(Employee) )
    employees = employees_records.scalars().all()

    # add permission flag dynamically
    employees_out = []
    for emp in employees:
        emp_data = GetMeSchema.from_orm(emp)
        emp_data.permission_flag = permission_flag(emp)
        employees_out.append(emp_data)
    return employees_out