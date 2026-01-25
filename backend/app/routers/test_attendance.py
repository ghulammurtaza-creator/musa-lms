"""
Test endpoint to manually create attendance logs for testing
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import List

from app.core.database import get_db
from app.models.models import Session, Teacher, Student, AttendanceLog, UserRole
from pydantic import BaseModel


router = APIRouter(prefix="/api/test", tags=["testing"])


class ManualAttendanceCreate(BaseModel):
    session_id: int
    user_email: str
    role: str  # "teacher" or "student"
    join_time: datetime
    exit_time: datetime = None


@router.post("/attendance/manual")
async def create_manual_attendance(
    attendance: ManualAttendanceCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Manually create attendance log for testing purposes
    """
    # Get session
    session_stmt = select(Session).where(Session.id == attendance.session_id)
    session_result = await db.execute(session_stmt)
    session = session_result.scalars().first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {attendance.session_id} not found"
        )
    
    # Find user
    teacher_id = None
    student_id = None
    
    if attendance.role == "teacher":
        teacher_stmt = select(Teacher).where(Teacher.email == attendance.user_email)
        teacher_result = await db.execute(teacher_stmt)
        teacher = teacher_result.scalars().first()
        if not teacher:
            raise HTTPException(status_code=404, detail=f"Teacher {attendance.user_email} not found")
        teacher_id = teacher.id
    else:
        student_stmt = select(Student).where(Student.email == attendance.user_email)
        student_result = await db.execute(student_stmt)
        student = student_result.scalars().first()
        if not student:
            raise HTTPException(status_code=404, detail=f"Student {attendance.user_email} not found")
        student_id = student.id
    
    # Calculate duration if exit time provided
    duration_minutes = None
    if attendance.exit_time:
        duration_minutes = (attendance.exit_time - attendance.join_time).total_seconds() / 60
    
    # Create attendance log
    attendance_log = AttendanceLog(
        session_id=attendance.session_id,
        user_email=attendance.user_email,
        role=UserRole.TEACHER if attendance.role == "teacher" else UserRole.STUDENT,
        teacher_id=teacher_id,
        student_id=student_id,
        join_time=attendance.join_time,
        exit_time=attendance.exit_time,
        duration_minutes=duration_minutes
    )
    
    db.add(attendance_log)
    await db.commit()
    await db.refresh(attendance_log)
    
    return {
        "message": "Attendance log created",
        "attendance_log": {
            "id": attendance_log.id,
            "session_id": attendance_log.session_id,
            "user_email": attendance_log.user_email,
            "role": attendance_log.role.value,
            "join_time": attendance_log.join_time,
            "exit_time": attendance_log.exit_time,
            "duration_minutes": attendance_log.duration_minutes
        }
    }


@router.post("/attendance/simulate-meeting/{session_id}")
async def simulate_meeting_attendance(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Simulate a complete meeting with teacher and student attendance
    """
    # Get session
    session_stmt = select(Session).where(Session.id == session_id)
    session_result = await db.execute(session_stmt)
    session = session_result.scalars().first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    # Get teacher
    teacher_stmt = select(Teacher).where(Teacher.id == session.teacher_id)
    teacher_result = await db.execute(teacher_stmt)
    teacher = teacher_result.scalars().first()
    
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    # Get students from scheduled class
    from app.models.models import ScheduledClass
    from sqlalchemy.orm import selectinload
    
    scheduled_stmt = select(ScheduledClass).options(
        selectinload(ScheduledClass.students)
    ).where(ScheduledClass.session_id == session_id)
    scheduled_result = await db.execute(scheduled_stmt)
    scheduled_class = scheduled_result.scalars().first()
    
    created_logs = []
    start_time = session.start_time
    
    # Create teacher attendance (joins 1 min early, stays for full duration)
    teacher_join = start_time - timedelta(minutes=1)
    teacher_exit = start_time + timedelta(minutes=scheduled_class.duration_minutes if scheduled_class else 30)
    
    teacher_log = AttendanceLog(
        session_id=session_id,
        user_email=teacher.email,
        role=UserRole.TEACHER,
        teacher_id=teacher.id,
        join_time=teacher_join,
        exit_time=teacher_exit,
        duration_minutes=(teacher_exit - teacher_join).total_seconds() / 60
    )
    db.add(teacher_log)
    created_logs.append({
        "user": teacher.email,
        "role": "teacher",
        "join": teacher_join,
        "exit": teacher_exit
    })
    
    # Create student attendance if scheduled class has students
    if scheduled_class:
        for student in scheduled_class.students:
            # Students join on time, leave 2 minutes early
            student_join = start_time
            student_exit = start_time + timedelta(minutes=scheduled_class.duration_minutes - 2)
            
            student_log = AttendanceLog(
                session_id=session_id,
                user_email=student.email,
                role=UserRole.STUDENT,
                student_id=student.id,
                join_time=student_join,
                exit_time=student_exit,
                duration_minutes=(student_exit - student_join).total_seconds() / 60
            )
            db.add(student_log)
            created_logs.append({
                "user": student.email,
                "role": "student",
                "join": student_join,
                "exit": student_exit
            })
    
    await db.commit()
    
    return {
        "message": f"Simulated attendance for {len(created_logs)} participants",
        "session_id": session_id,
        "attendance_logs": created_logs
    }
