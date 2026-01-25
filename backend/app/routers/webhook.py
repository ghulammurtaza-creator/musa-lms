from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.config import get_settings
from app.models.models import Session, AuthUser, AuthUserRole, AttendanceLog, UserRole
from app.schemas.schemas import GoogleMeetEvent
from app.services.duration_service import DurationCalculationEngine
from app.services.ai_service import ai_service
from app.services.google_meet_api import get_meet_service

router = APIRouter(prefix="/webhook", tags=["Webhook"])
settings = get_settings()


@router.post("/google-meet")
async def google_meet_webhook(
    event: GoogleMeetEvent,
    x_webhook_secret: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook endpoint to receive Google Meet join/exit events.
    Processes events and calculates durations.
    """
    # Verify webhook secret
    if x_webhook_secret != settings.google_webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook secret"
        )
    
    # Find or create session
    session_stmt = select(Session).where(Session.meeting_id == event.meeting_id)
    session_result = await db.execute(session_stmt)
    session = session_result.scalars().first()
    
    if not session:
        # If session doesn't exist and it's a join event for a teacher, create the session
        if event.event_type == "join" and event.role == UserRole.TEACHER:
            # Find teacher by email
            teacher_stmt = select(AuthUser).where(
                AuthUser.email == event.user_email,
                AuthUser.role == AuthUserRole.TUTOR
            )
            teacher_result = await db.execute(teacher_stmt)
            teacher = teacher_result.scalars().first()
            
            if not teacher:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Teacher with email {event.user_email} not found"
                )
            
            session = Session(
                meeting_id=event.meeting_id,
                teacher_id=teacher.id,
                start_time=event.timestamp
            )
            db.add(session)
            await db.commit()
            await db.refresh(session)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with meeting_id {event.meeting_id} not found"
            )
    
    # Process the event based on type
    if event.event_type == "join":
        # Determine if it's a teacher or student
        teacher_id = None
        student_id = None
        
        if event.role == UserRole.TEACHER:
            teacher_stmt = select(AuthUser).where(
                AuthUser.email == event.user_email,
                AuthUser.role == AuthUserRole.TUTOR
            )
            teacher_result = await db.execute(teacher_stmt)
            teacher = teacher_result.scalars().first()
            if teacher:
                teacher_id = teacher.id
        elif event.role == UserRole.STUDENT:
            student_stmt = select(AuthUser).where(
                AuthUser.email == event.user_email,
                AuthUser.role == AuthUserRole.STUDENT
            )
            student_result = await db.execute(student_stmt)
            student = student_result.scalars().first()
            if student:
                student_id = student.id
        
        # Process join event
        await DurationCalculationEngine.process_join_event(
            db=db,
            session_id=session.id,
            user_email=event.user_email,
            role=event.role,
            join_time=event.timestamp,
            teacher_id=teacher_id,
            student_id=student_id
        )
        
        return {
            "status": "success",
            "message": f"Join event processed for {event.user_email}",
            "session_id": session.id
        }
    
    elif event.event_type == "exit":
        # Process exit event
        attendance_log = await DurationCalculationEngine.process_exit_event(
            db=db,
            session_id=session.id,
            user_email=event.user_email,
            exit_time=event.timestamp
        )
        
        if not attendance_log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No active join event found for {event.user_email}"
            )
        
        # Check if this was the teacher leaving - if so, end the session
        if event.role == UserRole.TEACHER:
            session.end_time = event.timestamp
            await db.commit()
        
        return {
            "status": "success",
            "message": f"Exit event processed for {event.user_email}",
            "duration_minutes": attendance_log.duration_minutes
        }
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid event type: {event.event_type}"
        )


@router.post("/sessions/{session_id}/generate-summary")
async def generate_session_summary(
    session_id: int,
    transcript: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate AI summary for a session.
    Can provide transcript or generate from session metadata.
    """
    # Get session
    session_stmt = select(Session).where(Session.id == session_id)
    session_result = await db.execute(session_stmt)
    session = session_result.scalars().first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {session_id} not found"
        )
    
    if transcript:
        # Generate summary from transcript
        summary = await ai_service.generate_lesson_summary(transcript)
    else:
        # Generate summary from session metadata
        teacher_stmt = select(AuthUser).where(AuthUser.id == session.teacher_id)
        teacher_result = await db.execute(teacher_stmt)
        teacher = teacher_result.scalars().first()
        
        # Get all students in the session
        logs_stmt = select(AttendanceLog).where(
            AttendanceLog.session_id == session_id,
            AttendanceLog.role == UserRole.STUDENT
        )
        logs_result = await db.execute(logs_stmt)
        logs = logs_result.scalars().all()
        
        student_names = []
        for log in logs:
            if log.student_id:
                student_stmt = select(AuthUser).where(AuthUser.id == log.student_id)
                student_result = await db.execute(student_stmt)
                student = student_result.scalars().first()
                if student:
                    student_names.append(student.full_name)
        
        duration = 0
        if session.end_time:
            duration = (session.end_time - session.start_time).total_seconds() / 60
        
        summary = await ai_service.generate_session_notes(
            teacher_name=teacher.full_name if teacher else "Unknown",
            duration_minutes=duration,
            student_names=student_names
        )
    
    if summary:
        session.ai_summary = summary
        await db.commit()
        await db.refresh(session)
    
    return {
        "status": "success",
        "summary": summary,
        "session_id": session_id
    }


@router.post("/sessions/{session_id}/sync-participants")
async def sync_meeting_participants(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Sync actual participant data from Google Meet REST API.
    Call this after a meeting ends to get real join/leave times.
    Uses the official Google Meet API v2.
    """
    # Get session
    session_stmt = select(Session).where(Session.id == session_id)
    session_result = await db.execute(session_stmt)
    session = session_result.scalars().first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {session_id} not found"
        )
    
    if not session.google_meet_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session does not have a Google Meet code"
        )
    
    # Fetch actual participant data from Google Meet API
    try:
        meet_service = get_meet_service()
        meet_service.authenticate()
        
        # Get participant data using the Meet API
        participant_data = meet_service.get_meeting_participants(
            meet_code=session.google_meet_code
        )
        
        if not participant_data:
            return {
                "status": "no_data",
                "message": "No participant data found. Meeting may not have started yet or no conference record exists."
            }
        
        # Update attendance logs with real data
        updated_count = 0
        created_count = 0
        
        for participant in participant_data:
            email = participant.get('email')
            if not email:
                continue  # Skip anonymous/phone users without email
            
            sessions = participant.get('sessions', [])
            if not sessions:
                continue
            
            # Process each session (in case they joined multiple times)
            for session_data in sessions:
                join_time = session_data.get('start_time')
                leave_time = session_data.get('end_time')
                duration_seconds = session_data.get('duration_seconds', 0)
                
                if not join_time or not leave_time:
                    continue
                
                # Find existing attendance log or create new one
                log_stmt = select(AttendanceLog).where(
                    AttendanceLog.session_id == session_id,
                    AttendanceLog.user_email == email,
                    AttendanceLog.join_time >= join_time - timedelta(minutes=5),  # Allow some tolerance
                    AttendanceLog.join_time <= join_time + timedelta(minutes=5)
                ).order_by(AttendanceLog.join_time.desc())
                
                log_result = await db.execute(log_stmt)
                attendance_log = log_result.scalars().first()
                
                if attendance_log:
                    # Update existing log with real data
                    attendance_log.join_time = join_time
                    attendance_log.exit_time = leave_time
                    attendance_log.duration_minutes = round(duration_seconds / 60, 2)
                    updated_count += 1
                else:
                    # Create new attendance log
                    # Determine if teacher or student
                    teacher_stmt = select(AuthUser).where(
                        AuthUser.email == email,
                        AuthUser.role == AuthUserRole.TUTOR
                    )
                    teacher_result = await db.execute(teacher_stmt)
                    teacher = teacher_result.scalars().first()
                    
                    student_stmt = select(AuthUser).where(
                        AuthUser.email == email,
                        AuthUser.role == AuthUserRole.STUDENT
                    )
                    student_result = await db.execute(student_stmt)
                    student = student_result.scalars().first()
                    
                    new_log = AttendanceLog(
                        session_id=session_id,
                        user_email=email,
                        role=UserRole.TEACHER if teacher else UserRole.STUDENT,
                        teacher_id=teacher.id if teacher else None,
                        student_id=student.id if student else None,
                        join_time=join_time,
                        exit_time=leave_time,
                        duration_minutes=round(duration_seconds / 60, 2)
                    )
                    db.add(new_log)
                    created_count += 1
        
        await db.commit()
        
        return {
            "status": "success",
            "message": f"Synced {len(participant_data)} participants",
            "updated": updated_count,
            "created": created_count,
            "participants": participant_data
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing participants: {str(e)}"
        )
