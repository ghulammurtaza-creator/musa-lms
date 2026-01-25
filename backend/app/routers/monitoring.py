from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List
from app.core.database import get_db
from app.schemas.schemas import (
    ActiveSessionResponse, 
    FamilyBilling, 
    TeacherPayroll,
    AttendanceLogResponse,
    UserSessionReport,
    UserSessionDetail
)
from app.services.duration_service import DurationCalculationEngine
from app.services.billing_service import BillingService
from app.services.meeting_monitor import get_monitor_service
from sqlalchemy import select
from app.models.models import AttendanceLog, ScheduledClass, Session

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


@router.post("/sync-participants/{class_id}")
async def sync_class_participants(
    class_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger participant data sync for a specific scheduled class.
    Useful for forcing an update or testing the automated system.
    """
    # Get scheduled class with students relationship eagerly loaded
    from sqlalchemy.orm import selectinload
    
    stmt = select(ScheduledClass).options(
        selectinload(ScheduledClass.students)
    ).where(ScheduledClass.id == class_id)
    result = await db.execute(stmt)
    scheduled_class = result.scalars().first()
    
    if not scheduled_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheduled class {class_id} not found"
        )
    
    if not scheduled_class.google_meet_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Class does not have a Google Meet code"
        )
    
    if not scheduled_class.session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Class does not have an active session yet"
        )
    
    # Get session
    session_stmt = select(Session).where(Session.id == scheduled_class.session_id)
    session_result = await db.execute(session_stmt)
    session = session_result.scalars().first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {scheduled_class.session_id} not found"
        )
    
    # Trigger sync
    monitor_service = get_monitor_service()
    await monitor_service.sync_participant_data(db, session, scheduled_class)
    await db.commit()
    
    # Return updated attendance logs
    attendance_stmt = select(AttendanceLog).where(
        AttendanceLog.session_id == session.id
    ).order_by(AttendanceLog.join_time)
    attendance_result = await db.execute(attendance_stmt)
    logs = attendance_result.scalars().all()
    
    return {
        "message": "Participant data synced successfully",
        "class_id": class_id,
        "session_id": session.id,
        "meet_code": scheduled_class.google_meet_code,
        "attendance_logs": [
            {
                "id": log.id,
                "user_email": log.user_email,
                "role": log.role.value,
                "join_time": log.join_time,
                "exit_time": log.exit_time,
                "duration_minutes": log.duration_minutes
            }
            for log in logs
        ]
    }


@router.post("/sync-all-active")
async def sync_all_active_participants(
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger participant data sync for all active classes.
    This is the same operation that runs automatically every 3 minutes.
    """
    monitor_service = get_monitor_service()
    await monitor_service.fetch_participant_data()
    
    return {
        "message": "Triggered participant sync for all active classes",
        "note": "This operation runs automatically every 3 minutes"
    }


@router.get("/user-sessions", response_model=List[UserSessionReport])
async def get_user_sessions(
    year: int = Query(..., description="Year for report (e.g., 2026)"),
    month: int = Query(..., ge=1, le=12, description="Month for report (1-12)"),
    role: str = Query(None, description="Filter by role: 'tutor' or 'student'"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all users with their session details for a specific month.
    Returns tutors and students with their attendance logs.
    """
    from app.models.models import AuthUser, AuthUserRole
    from datetime import datetime
    from sqlalchemy import and_
    
    # Calculate date range for the month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    # Build query for users
    user_query = select(AuthUser)
    
    # Filter by role if specified
    if role:
        if role.lower() == 'tutor':
            user_query = user_query.where(AuthUser.role == AuthUserRole.TUTOR)
        elif role.lower() == 'student':
            user_query = user_query.where(AuthUser.role == AuthUserRole.STUDENT)
    else:
        # Get both tutors and students
        user_query = user_query.where(
            AuthUser.role.in_([AuthUserRole.TUTOR, AuthUserRole.STUDENT])
        )
    
    user_result = await db.execute(user_query)
    users = user_result.scalars().all()
    
    user_reports = []
    
    for user in users:
        # Get attendance logs for this user in the specified month
        logs_query = select(AttendanceLog).where(
            and_(
                AttendanceLog.user_email == user.email,
                AttendanceLog.join_time >= start_date,
                AttendanceLog.join_time < end_date
            )
        ).order_by(AttendanceLog.join_time.desc())
        
        logs_result = await db.execute(logs_query)
        logs = logs_result.scalars().all()
        
        # Calculate totals
        total_sessions = len(logs)
        total_minutes = sum(log.duration_minutes or 0 for log in logs)
        
        # Build session details
        session_details = [
            UserSessionDetail(
                session_id=log.session_id,
                join_time=log.join_time,
                exit_time=log.exit_time,
                duration_minutes=log.duration_minutes or 0
            )
            for log in logs
        ]
        
        # Create user report
        user_reports.append(UserSessionReport(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
            total_sessions=total_sessions,
            total_minutes=total_minutes,
            sessions=session_details
        ))
    
    return user_reports
