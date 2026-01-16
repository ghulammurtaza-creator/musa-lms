"""
Simplified endpoint to sync Google Meet participants using teacher's OAuth credentials
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import HttpRequest
from datetime import datetime
import json
import httplib2

from app.core.database import get_db
from app.models.models import Session, Teacher, Student, AttendanceLog, UserRole

router = APIRouter(prefix="/sync", tags=["Sync"])


def build_meet_service(credentials):
    """Build Meet API service with static discovery"""
    # Use the REST discovery URL for Meet API v2
    discovery_url = 'https://meet.googleapis.com/$discovery/rest?version=v2'
    
    # Build service with discovery URL
    http = credentials.authorize(httplib2.Http())
    return build(
        'meet',
        'v2',
        http=http,
        discoveryServiceUrl=discovery_url,
        static_discovery=False
    )


@router.post("/sessions/{session_id}/participants")
async def sync_session_participants(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Sync participants from Google Meet for a specific session.
    Uses the teacher's OAuth credentials to access the Meet API v2.
    """
    # Get session with teacher
    session_stmt = select(Session).where(Session.id == session_id)
    session_result = await db.execute(session_stmt)
    session = session_result.scalars().first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get teacher with credentials
    teacher_stmt = select(Teacher).where(Teacher.id == session.teacher_id)
    teacher_result = await db.execute(teacher_stmt)
    teacher = teacher_result.scalars().first()
    
    if not teacher or not teacher.google_credentials:
        raise HTTPException(
            status_code=400,
            detail="Teacher does not have Google credentials. Please connect Google Calendar first."
        )
    
    if not session.google_meet_code:
        raise HTTPException(
            status_code=400,
            detail="Session does not have a Google Meet code"
        )
    
    try:
        # Parse teacher's credentials
        creds_dict = json.loads(teacher.google_credentials)
        credentials = Credentials(
            token=creds_dict.get('token'),
            refresh_token=creds_dict.get('refresh_token'),
            token_uri=creds_dict.get('token_uri'),
            client_id=creds_dict.get('client_id'),
            client_secret=creds_dict.get('client_secret'),
            scopes=creds_dict.get('scopes')
        )
        
        # Build Meet API service
        try:
            service = build_meet_service(credentials)
        except Exception as api_error:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to build Meet API service: {str(api_error)}. "
                       "Make sure Google Meet API is enabled in your Google Cloud Console."
            )
        
        # Get conference record by meet code
        meet_code = session.google_meet_code
        response = service.conferenceRecords().list(
            filter=f'space.meeting_code="{meet_code}"',
            pageSize=10
        ).execute()
        
        records = response.get('conferenceRecords', [])
        
        if not records:
            return {
                "status": "no_data",
                "message": f"No conference record found for meet code: {meet_code}. The meeting may not have started yet, or data is not yet available (can take a few minutes after meeting starts)."
            }
        
        # Get the conference record
        conference_record_name = records[0].get('name')
        
        # Get all participants
        participants_response = service.conferenceRecords().participants().list(
            parent=conference_record_name,
            pageSize=100
        ).execute()
        
        participants = participants_response.get('participants', [])
        
        if not participants:
            return {
                "status": "no_participants",
                "message": "Conference record found but no participants yet."
            }
        
        created_count = 0
        updated_count = 0
        
        for participant in participants:
            participant_name = participant.get('name')
            
            # Get user email
            signed_in_user = participant.get('signedinUser', {})
            email = signed_in_user.get('user', '').replace('users/', '')
            
            if not email:
                continue  # Skip anonymous users
            
            # Get participant sessions
            try:
                sessions_response = service.conferenceRecords().participants().participantSessions().list(
                    parent=participant_name,
                    pageSize=100
                ).execute()
                
                sessions = sessions_response.get('participantSessions', [])
                
                for p_session in sessions:
                    start_time_str = p_session.get('startTime')
                    end_time_str = p_session.get('endTime')
                    
                    if not start_time_str:
                        continue
                    
                    start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                    end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00')) if end_time_str else None
                    
                    duration_minutes = None
                    if start_time and end_time:
                        duration_minutes = (end_time - start_time).total_seconds() / 60
                    
                    # Check if log already exists
                    log_stmt = select(AttendanceLog).where(
                        AttendanceLog.session_id == session_id,
                        AttendanceLog.user_email == email,
                        AttendanceLog.join_time == start_time
                    )
                    log_result = await db.execute(log_stmt)
                    existing_log = log_result.scalars().first()
                    
                    if existing_log:
                        # Update existing log
                        existing_log.exit_time = end_time
                        existing_log.duration_minutes = duration_minutes
                        updated_count += 1
                    else:
                        # Determine role
                        teacher_check = select(Teacher).where(Teacher.email == email)
                        teacher_check_result = await db.execute(teacher_check)
                        is_teacher = teacher_check_result.scalars().first()
                        
                        student_check = select(Student).where(Student.email == email)
                        student_check_result = await db.execute(student_check)
                        student = student_check_result.scalars().first()
                        
                        # Create new log
                        new_log = AttendanceLog(
                            session_id=session_id,
                            user_email=email,
                            role=UserRole.TEACHER if is_teacher else UserRole.STUDENT,
                            teacher_id=is_teacher.id if is_teacher else None,
                            student_id=student.id if student else None,
                            join_time=start_time,
                            exit_time=end_time,
                            duration_minutes=duration_minutes
                        )
                        db.add(new_log)
                        created_count += 1
                        
            except Exception as e:
                print(f"Error getting sessions for participant {email}: {e}")
                continue
        
        await db.commit()
        
        return {
            "status": "success",
            "message": f"Synced {len(participants)} participants",
            "participants_found": len(participants),
            "logs_created": created_count,
            "logs_updated": updated_count
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error syncing participants: {str(e)}"
        )
