"""
API Router for scheduling classes with Google Calendar/Meet integration
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, timedelta, timezone

from app.core.database import get_db
from app.models.models import ScheduledClass, Teacher, Student, Session, AuthUser, AuthUserRole
from app.schemas.schemas import (
    ScheduledClassCreate,
    ScheduledClassUpdate,
    ScheduledClassResponse,
    ScheduledClassWithDetails
)
from app.services.google_calendar_helper import create_class_event, update_class_event, cancel_class_event


router = APIRouter(prefix="/api/schedule", tags=["scheduling"])


async def get_shared_google_credentials(db: AsyncSession) -> dict:
    """
    Get shared Google credentials from a service account (admin user).
    This allows using one paid Google Workspace account for all teachers.
    
    Returns the google_credentials JSON from the admin account.
    """
    # Try to get admin account with google credentials
    admin_stmt = select(AuthUser).where(
        AuthUser.role == AuthUserRole.ADMIN,
        AuthUser.google_credentials.isnot(None)
    ).limit(1)
    admin_result = await db.execute(admin_stmt)
    admin = admin_result.scalars().first()
    
    if admin and admin.google_credentials:
        return admin.google_credentials
    
    # If no admin, try to get any tutor with credentials (fallback)
    tutor_stmt = select(AuthUser).where(
        AuthUser.role == AuthUserRole.TUTOR,
        AuthUser.google_credentials.isnot(None)
    ).limit(1)
    tutor_result = await db.execute(tutor_stmt)
    tutor = tutor_result.scalars().first()
    
    if tutor and tutor.google_credentials:
        return tutor.google_credentials
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="No Google Calendar connection found. Admin must connect Google Calendar first."
    )


@router.post("/class", response_model=ScheduledClassResponse, status_code=status.HTTP_201_CREATED)
async def schedule_class(
    class_data: ScheduledClassCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Schedule a new class with Google Calendar and Meet integration
    
    Uses shared Google Workspace credentials (from admin account) to create meetings
    for all teachers, reducing licensing costs while still tracking individual teachers.
    
    Steps:
    1. Validate teacher exists (no OAuth required per teacher)
    2. Validate all students exist
    3. Get shared Google credentials
    4. Create Google Calendar event with Meet link
    5. Store scheduled class in database with correct teacher_id
    6. Return class details with Meet link
    """
    
    # 1. Get teacher (check AuthUser table)
    teacher_stmt = select(AuthUser).where(AuthUser.email == class_data.teacher_email)
    teacher_result = await db.execute(teacher_stmt)
    teacher = teacher_result.scalars().first()
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with email {class_data.teacher_email} not found"
        )
    
    # Verify user is a teacher/tutor
    if teacher.role != AuthUserRole.TUTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tutors can schedule classes"
        )
    
    # 2. Validate all students exist (check AuthUser table)
    students = []
    for student_email in class_data.student_emails:
        student_stmt = select(AuthUser).where(AuthUser.email == student_email)
        student_result = await db.execute(student_stmt)
        student = student_result.scalars().first()
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with email {student_email} not found"
            )
        
        # Verify user is a student
        if student.role != AuthUserRole.STUDENT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{student_email} is not a student"
            )
        students.append(student)
    
    # 3. Get shared Google credentials (from admin/service account)
    shared_credentials = await get_shared_google_credentials(db)
    
    # 4. Create Google Calendar event with Meet using shared credentials
    try:
        event_data = create_class_event(
            teacher_credentials_json=shared_credentials,
            teacher_email=class_data.teacher_email,  # Still shows correct teacher in meeting
            student_emails=class_data.student_emails,
            subject=class_data.subject,
            start_time=class_data.start_time,
            duration_minutes=class_data.duration_minutes,
            description=class_data.description or ""
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Google Calendar event: {str(e)}"
        )
    
    # 4. Create scheduled class in database
    scheduled_class = ScheduledClass(
        teacher_id=teacher.id,
        subject=class_data.subject,
        start_time=class_data.start_time,
        end_time=datetime.fromisoformat(event_data['end_time'].replace('Z', '+00:00')),
        duration_minutes=class_data.duration_minutes,
        google_calendar_event_id=event_data['event_id'],
        google_meet_link=event_data['meet_link'],
        google_meet_code=event_data['meet_code'],
        is_active=False,
        is_completed=False
    )
    
    # Add students to the class
    scheduled_class.students = students
    
    db.add(scheduled_class)
    await db.flush()  # Get the ID
    
    # 5. If meeting starts within 5 minutes, create session immediately
    now_utc = datetime.now(timezone.utc)
    start_time_utc = class_data.start_time
    if start_time_utc.tzinfo is None:
        start_time_utc = start_time_utc.replace(tzinfo=timezone.utc)
    
    time_until_start = (start_time_utc - now_utc).total_seconds()
    if -60 <= time_until_start <= 300:  # Between 1 min ago and 5 min in future
        session = Session(
            meeting_id=event_data['meet_code'] or f"scheduled-{scheduled_class.id}",
            teacher_id=teacher.id,
            start_time=class_data.start_time,
            is_scheduled=True,
            google_meet_code=event_data['meet_code'],
            google_calendar_event_id=event_data['event_id']
        )
        db.add(session)
        await db.flush()
        
        scheduled_class.session_id = session.id
        scheduled_class.is_active = True
        print(f"Created session {session.id} for immediate/upcoming class {scheduled_class.id}")
    
    await db.commit()
    await db.refresh(scheduled_class)
    
    return scheduled_class


@router.get("/classes", response_model=List[ScheduledClassWithDetails])
async def get_scheduled_classes(
    teacher_email: str = None,
    student_email: str = None,
    upcoming_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """
    Get scheduled classes filtered by teacher or student
    
    Args:
        teacher_email: Filter by teacher email
        student_email: Filter by student email
        upcoming_only: Only return future classes (default: True)
    """
    
    stmt = select(ScheduledClass)
    
    # Filter by teacher
    if teacher_email:
        teacher_stmt = select(AuthUser).where(AuthUser.email == teacher_email)
        teacher_result = await db.execute(teacher_stmt)
        teacher = teacher_result.scalars().first()
        if teacher:
            stmt = stmt.where(ScheduledClass.teacher_id == teacher.id)
    
    # Filter by student
    if student_email:
        student_stmt = select(AuthUser).where(AuthUser.email == student_email)
        student_result = await db.execute(student_stmt)
        student = student_result.scalars().first()
        if student:
            stmt = stmt.join(ScheduledClass.students).where(Student.id == student.id)
    
    # Filter upcoming only
    if upcoming_only:
        stmt = stmt.where(ScheduledClass.start_time > datetime.utcnow())
    
    stmt = stmt.order_by(ScheduledClass.start_time)
    
    result = await db.execute(stmt)
    classes = result.scalars().all()
    
    return classes


@router.get("/class/{class_id}", response_model=ScheduledClassWithDetails)
async def get_scheduled_class(
    class_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific scheduled class"""
    
    stmt = select(ScheduledClass).where(ScheduledClass.id == class_id)
    result = await db.execute(stmt)
    scheduled_class = result.scalars().first()
    
    if not scheduled_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheduled class with ID {class_id} not found"
        )
    
    return scheduled_class


@router.put("/class/{class_id}", response_model=ScheduledClassResponse)
async def update_scheduled_class(
    class_id: int,
    update_data: ScheduledClassUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a scheduled class
    Updates both database and Google Calendar event
    """
    
    # Get existing class
    stmt = select(ScheduledClass).where(ScheduledClass.id == class_id)
    result = await db.execute(stmt)
    scheduled_class = result.scalars().first()
    
    if not scheduled_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheduled class with ID {class_id} not found"
        )
    
    # Update Google Calendar event
    try:
        calendar_service = get_calendar_service()
        calendar_service.update_class_event(
            event_id=scheduled_class.google_calendar_event_id,
            start_time=update_data.start_time,
            duration_minutes=update_data.duration_minutes,
            student_emails=update_data.student_emails
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update Google Calendar event: {str(e)}"
        )
    
    # Update database
    if update_data.start_time:
        scheduled_class.start_time = update_data.start_time
    
    if update_data.duration_minutes:
        from datetime import timedelta
        scheduled_class.duration_minutes = update_data.duration_minutes
        scheduled_class.end_time = scheduled_class.start_time + timedelta(minutes=update_data.duration_minutes)
    
    if update_data.student_emails:
        # Update students
        students = []
        for student_email in update_data.student_emails:
            student_stmt = select(Student).where(Student.email == student_email)
            student_result = await db.execute(student_stmt)
            student = student_result.scalars().first()
            if student:
                students.append(student)
        scheduled_class.students = students
    
    await db.commit()
    await db.refresh(scheduled_class)
    
    return scheduled_class


@router.delete("/class/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_scheduled_class(
    class_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel a scheduled class
    Deletes both database record and Google Calendar event
    """
    
    # Get existing class
    stmt = select(ScheduledClass).where(ScheduledClass.id == class_id)
    result = await db.execute(stmt)
    scheduled_class = result.scalars().first()
    
    if not scheduled_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheduled class with ID {class_id} not found"
        )
    
    # Cancel Google Calendar event
    try:
        calendar_service = get_calendar_service()
        calendar_service.cancel_class_event(
            event_id=scheduled_class.google_calendar_event_id
        )
    except Exception as e:
        # Log error but continue with database deletion
        print(f"Warning: Failed to cancel Google Calendar event: {str(e)}")
    
    # Delete from database
    await db.delete(scheduled_class)
    await db.commit()
    
    return None
