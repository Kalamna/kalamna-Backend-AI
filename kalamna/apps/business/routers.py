"""
Authentication API routes
Endpoints: /login, /register, /refresh, /logout, /me
"""
from datetime import datetime, timezone
from fastapi import APIRouter,Depends, HTTPException, status
from .models import Business
from kalamna.apps.employees.models import Employee
from .schemas import LoginSchema, GetMeSchema
from .services import verify_password, permission_flag
from ...core import db
from kalamna.core.security import create_access_token, create_refresh_token
from kalamna.core.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

router = APIRouter(
    prefix='/business',
    tags=['Business']
)


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


@router.post("/login")
async def login(data: LoginSchema, db: AsyncSession = Depends(get_db)):
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

    # Generate tokens using existing JWT builder
    access_token = create_access_token(
        employee_id=str(employee.id),
        role=str(employee.role)
    )
    refresh_token = create_refresh_token(employee_id=str(employee.id))

    return {
        "access": access_token,
        "refresh": refresh_token,
        "message": "login success",
        "token expire time": "access : 15 minutes, refresh: 7 days"
    }

