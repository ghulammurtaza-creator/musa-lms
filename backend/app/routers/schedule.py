"""
API Router for scheduling classes with Google Calendar/Meet integration
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, timedelta, timezone

from app.core.database import get_db
from app.models.models import ScheduledClass, Teacher, Student, Session
from app.schemas.schemas import (
    ScheduledClassCreate,
    ScheduledClassUpdate,
    ScheduledClassResponse,
    ScheduledClassWithDetails
)
from app.services.google_calendar_helper import create_class_event, update_class_event, cancel_class_event


router = APIRouter(prefix="/api/schedule", tags=["scheduling"])


@router.post("/class", response_model=ScheduledClassResponse, status_code=status.HTTP_201_CREATED)
async def schedule_class(
    class_data: ScheduledClassCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Schedule a new class with Google Calendar and Meet integration
    
    Steps:
    1. Validate teacher exists and has connected Google Calendar
    2. Validate all students exist
    3. Create Google Calendar event with Meet link
    4. Store scheduled class in database
    5. Return class details with Meet link
    """
    
    # 1. Get teacher and check OAuth connection
    teacher_stmt = select(Teacher).where(Teacher.email == class_data.teacher_email)
    teacher_result = await db.execute(teacher_stmt)
    teacher = teacher_result.scalars().first()
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with email {class_data.teacher_email} not found"
        )
    
    if not teacher.google_credentials:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Teacher must connect Google Calendar first. Please use the 'Connect Google Calendar' button."
        )
    
    # 2. Validate all students exist
    students = []
    for student_email in class_data.student_emails:
        student_stmt = select(Student).where(Student.email == student_email)
        student_result = await db.execute(student_stmt)
        student = student_result.scalars().first()
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with email {student_email} not found"
            )
        students.append(student)
    
    # 3. Create Google Calendar event with Meet using teacher's credentials
    try:
        event_data = create_class_event(
            teacher_credentials_json=teacher.google_credentials,
            teacher_email=class_data.teacher_email,
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
        teacher_stmt = select(Teacher).where(Teacher.email == teacher_email)
        teacher_result = await db.execute(teacher_stmt)
        teacher = teacher_result.scalars().first()
        if teacher:
            stmt = stmt.where(ScheduledClass.teacher_id == teacher.id)
    
    # Filter by student
    if student_email:
        student_stmt = select(Student).where(Student.email == student_email)
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
