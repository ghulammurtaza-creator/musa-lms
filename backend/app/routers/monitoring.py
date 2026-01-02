from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List
from app.core.database import get_db
from app.schemas.schemas import (
    ActiveSessionResponse, 
    FamilyBilling, 
    TeacherPayroll,
    AttendanceLogResponse
)
from app.services.duration_service import DurationCalculationEngine
from app.services.billing_service import BillingService
from sqlalchemy import select
from app.models.models import AttendanceLog

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


@router.get("/active-sessions", response_model=List[ActiveSessionResponse])
async def get_active_sessions(db: AsyncSession = Depends(get_db)):
    """
    Get all currently active sessions with real-time participant information.
    """
    active_sessions = await DurationCalculationEngine.get_active_sessions(db)
    
    return [
        ActiveSessionResponse(
            session_id=session['session_id'],
            meeting_id=session['meeting_id'],
            teacher_name=session['teacher_name'],
            start_time=session['start_time'],
            participants=session['participants']
        )
        for session in active_sessions
    ]


@router.get("/attendance-logs", response_model=List[AttendanceLogResponse])
async def get_attendance_logs(
    skip: int = 0,
    limit: int = 100,
    session_id: int = None,
    user_email: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get attendance logs with optional filtering.
    """
    stmt = select(AttendanceLog)
    
    if session_id:
        stmt = stmt.where(AttendanceLog.session_id == session_id)
    
    if user_email:
        stmt = stmt.where(AttendanceLog.user_email == user_email)
    
    stmt = stmt.offset(skip).limit(limit).order_by(AttendanceLog.join_time.desc())
    
    result = await db.execute(stmt)
    logs = result.scalars().all()
    
    return logs


@router.get("/billing/families", response_model=List[FamilyBilling])
async def get_all_families_billing(
    year: int = Query(..., description="Year for billing (e.g., 2026)"),
    month: int = Query(..., ge=1, le=12, description="Month for billing (1-12)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate billing reports for all families for a specific month.
    """
    billings = await BillingService.calculate_all_families_billing(db, year, month)
    return billings


@router.get("/billing/families/{family_id}", response_model=FamilyBilling)
async def get_family_billing(
    family_id: int,
    year: int = Query(..., description="Year for billing (e.g., 2026)"),
    month: int = Query(..., ge=1, le=12, description="Month for billing (1-12)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate billing report for a specific family for a specific month.
    """
    billing = await BillingService.calculate_family_billing(db, family_id, year, month)
    return billing


@router.get("/payroll/teachers", response_model=List[TeacherPayroll])
async def get_all_teachers_payroll(
    year: int = Query(..., description="Year for payroll (e.g., 2026)"),
    month: int = Query(..., ge=1, le=12, description="Month for payroll (1-12)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate payroll reports for all teachers for a specific month.
    """
    payrolls = await BillingService.calculate_all_teachers_payroll(db, year, month)
    return payrolls


@router.get("/payroll/teachers/{teacher_id}", response_model=TeacherPayroll)
async def get_teacher_payroll(
    teacher_id: int,
    year: int = Query(..., description="Year for payroll (e.g., 2026)"),
    month: int = Query(..., ge=1, le=12, description="Month for payroll (1-12)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate payroll report for a specific teacher for a specific month.
    """
    payroll = await BillingService.calculate_teacher_payroll(db, teacher_id, year, month)
    return payroll
