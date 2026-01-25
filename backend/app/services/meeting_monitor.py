"""
Background monitoring service for active Google Meet sessions
Uses APScheduler to periodically check scheduled classes and track attendance
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from typing import List, Dict
import asyncio
import json

from app.core.database import AsyncSessionLocal
from app.models.models import ScheduledClass, Session, AttendanceLog, AuthUser, AuthUserRole, UserRole
from app.services.duration_service import DurationCalculationEngine
from app.services.google_meet_api import GoogleMeetAPIService


class MeetingMonitorService:
    """Service to monitor active Google Meet sessions"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        self.meet_service = None
    
    def _get_meet_service(self) -> GoogleMeetAPIService:
        """Get or initialize Google Meet service"""
        if self.meet_service is None:
            try:
                self.meet_service = GoogleMeetAPIService()
                self.meet_service.authenticate()
                print("Google Meet API service initialized")
            except Exception as e:
                print(f"Warning: Failed to initialize Google Meet API: {e}")
                self.meet_service = None
        return self.meet_service
    
    def start(self):
        """Start the monitoring service"""
        if not self.is_running:
            # Schedule monitoring every 2 minutes
            self.scheduler.add_job(
                self.monitor_active_classes,
                IntervalTrigger(seconds=120),  # Check every 2 minutes
                id='monitor_classes',
                replace_existing=True
            )
            
            # Schedule participant data fetching every 3 minutes
            self.scheduler.add_job(
                self.fetch_participant_data,
                IntervalTrigger(seconds=180),  # Fetch every 3 minutes
                id='fetch_participants',
                replace_existing=True
            )
            
            # Schedule retry for failed fetches every 10 minutes
            self.scheduler.add_job(
                self.retry_failed_fetches,
                IntervalTrigger(seconds=600),  # Retry every 10 minutes
                id='retry_failed',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            print("Meeting monitoring service started with automated participant tracking")
    
    def stop(self):
        """Stop the monitoring service"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            print("Meeting monitoring service stopped")
    
    async def monitor_active_classes(self):
        """
        Check for classes that should be active now
        and create/update sessions accordingly
        """
        async with AsyncSessionLocal() as db:
            try:
                now = datetime.utcnow()
                
                # Find classes that should be active (started but not ended)
                stmt = select(ScheduledClass).where(
                    ScheduledClass.start_time <= now,
                    ScheduledClass.end_time >= now,
                    ScheduledClass.is_completed == False
                )
                
                result = await db.execute(stmt)
                active_classes = result.scalars().all()
                
                for scheduled_class in active_classes:
                    await self.process_active_class(db, scheduled_class)
                
                # Find classes that have ended
                stmt = select(ScheduledClass).where(
                    ScheduledClass.end_time < now,
                    ScheduledClass.is_completed == False
                )
                
                result = await db.execute(stmt)
                ended_classes = result.scalars().all()
                
                for scheduled_class in ended_classes:
                    await self.complete_class(db, scheduled_class)
                
                await db.commit()
                
            except Exception as e:
                print(f"Error monitoring classes: {e}")
                await db.rollback()
    
    async def process_active_class(self, db: AsyncSession, scheduled_class: ScheduledClass):
        """
        Process an active class:
        1. Create session if doesn't exist
        2. Mark class as active
        """
        if not scheduled_class.is_active:
            # Create session for this class
            if not scheduled_class.session_id:
                session = Session(
                    meeting_id=scheduled_class.google_meet_code or f"scheduled-{scheduled_class.id}",
                    teacher_id=scheduled_class.teacher_id,
                    start_time=scheduled_class.start_time,
                    is_scheduled=True,
                    google_meet_code=scheduled_class.google_meet_code,
                    google_calendar_event_id=scheduled_class.google_calendar_event_id
                )
                db.add(session)
                await db.flush()
                
                scheduled_class.session_id = session.id
            
            scheduled_class.is_active = True
            print(f"Class {scheduled_class.id} ({scheduled_class.subject}) is now active")
    
    async def complete_class(self, db: AsyncSession, scheduled_class: ScheduledClass):
        """
        Mark class as completed and close the session
        Also fetch final participant data from Google Meet API
        """
        if scheduled_class.session_id:
            # Get the session
            session_stmt = select(Session).where(Session.id == scheduled_class.session_id)
            session_result = await db.execute(session_stmt)
            session = session_result.scalars().first()
            
            if session and not session.end_time:
                session.end_time = scheduled_class.end_time
                
                # Fetch final participant data from Google Meet API
                if scheduled_class.google_meet_code:
                    print(f"Fetching final participant data for meeting {scheduled_class.google_meet_code}")
                    await self.sync_participant_data(db, session, scheduled_class)
                
                # Process any open attendance logs (students who didn't exit)
                attendance_stmt = select(AttendanceLog).where(
                    AttendanceLog.session_id == session.id,
                    AttendanceLog.exit_time.is_(None)
                )
                attendance_result = await db.execute(attendance_stmt)
                open_logs = attendance_result.scalars().all()
                
                for log in open_logs:
                    # Auto-exit at class end time
                    log.exit_time = scheduled_class.end_time
                    duration = (log.exit_time - log.join_time).total_seconds() / 60
                    log.duration_minutes = round(duration, 2)
        
        scheduled_class.is_active = False
        scheduled_class.is_completed = True
        print(f"Class {scheduled_class.id} ({scheduled_class.subject}) completed")
    
    async def fetch_participant_data(self):
        """
        Periodically fetch participant data for all active meetings
        and create/update attendance logs automatically
        """
        async with AsyncSessionLocal() as db:
            try:
                now = datetime.utcnow()
                
                # Find all active scheduled classes with Meet codes
                stmt = select(ScheduledClass).options(
                    selectinload(ScheduledClass.students)
                ).where(
                    ScheduledClass.is_active == True,
                    ScheduledClass.is_completed == False,
                    ScheduledClass.google_meet_code.isnot(None)
                )
                
                result = await db.execute(stmt)
                active_classes = result.scalars().all()
                
                if not active_classes:
                    print("No active classes to fetch participant data for")
                    return
                
                print(f"Fetching participant data for {len(active_classes)} active classes...")
                
                for scheduled_class in active_classes:
                    # Get or create session
                    if scheduled_class.session_id:
                        session_stmt = select(Session).where(Session.id == scheduled_class.session_id)
                        session_result = await db.execute(session_stmt)
                        session = session_result.scalars().first()
                        
                        if session:
                            # Reload the scheduled_class with students to avoid lazy loading
                            class_stmt = select(ScheduledClass).options(
                                selectinload(ScheduledClass.students)
                            ).where(ScheduledClass.id == scheduled_class.id)
                            class_result = await db.execute(class_stmt)
                            scheduled_class_with_students = class_result.scalars().first()
                            
                            if scheduled_class_with_students:
                                await self.sync_participant_data(db, session, scheduled_class_with_students)
                
                await db.commit()
                print("Participant data fetch completed")
                
            except Exception as e:
                print(f"Error fetching participant data: {e}")
                await db.rollback()
    
    async def sync_participant_data(
        self,
        db: AsyncSession,
        session: Session,
        scheduled_class: ScheduledClass
    ):
        """
        Fetch participant data from Google Meet API and sync with attendance logs.
        Uses shared Google credentials (from admin) to fetch data for all teachers' meetings.
        """
        try:
            # Get shared Google credentials from admin account
            admin_stmt = select(AuthUser).where(
                AuthUser.role == AuthUserRole.ADMIN,
                AuthUser.google_credentials.isnot(None)
            ).limit(1)
            admin_result = await db.execute(admin_stmt)
            admin = admin_result.scalars().first()
            
            if not admin:
                # Fallback: try to get any tutor with credentials
                tutor_stmt = select(AuthUser).where(
                    AuthUser.role == AuthUserRole.TUTOR,
                    AuthUser.google_credentials.isnot(None)
                ).limit(1)
                tutor_result = await db.execute(tutor_stmt)
                admin = tutor_result.scalars().first()
            
            if not admin or not admin.google_credentials:
                print("No shared Google credentials found. Admin must connect Google Calendar.")
                return
            
            # Create Meet service with shared credentials
            meet_service = GoogleMeetAPIService(credentials_dict=admin.google_credentials)
            meet_service.authenticate()
            
            # Fetch participants from Google Meet API
            participants = meet_service.get_meeting_participants(
                meet_code=scheduled_class.google_meet_code
            )
            
            if not participants:
                print(f"No participant data available yet for meeting {scheduled_class.google_meet_code}")
                return
            
            print(f"Found {len(participants)} participants for meeting {scheduled_class.google_meet_code}")
            
            # Get teacher (from AuthUser with tutor role) - for matching attendance
            teacher_stmt = select(AuthUser).where(
                AuthUser.id == scheduled_class.teacher_id,
                AuthUser.role == AuthUserRole.TUTOR
            )
            teacher_result = await db.execute(teacher_stmt)
            teacher = teacher_result.scalars().first()
            
            # DEBUG: Print teacher and student names from database
            if teacher:
                print(f"📋 Teacher in DB: '{teacher.full_name}' (ID: {teacher.id})")
            else:
                print(f"⚠️ No teacher found for class {scheduled_class.id}")
            
            print(f"📋 Enrolled students ({len(scheduled_class.students)}):")
            for student in scheduled_class.students:
                print(f"   - '{student.full_name}' (ID: {student.id})")
            
            # Get existing attendance logs for this session
            attendance_stmt = select(AttendanceLog).where(
                AttendanceLog.session_id == session.id
            )
            attendance_result = await db.execute(attendance_stmt)
            existing_logs = {log.user_email: log for log in attendance_result.scalars().all()}
            
            # Process each participant
            for participant_data in participants:
                email = participant_data.get('email')
                display_name = participant_data.get('display_name', 'Unknown')
                if not email or not display_name:
                    continue
                
                # Normalize for matching (lowercase, remove spaces and dots)
                display_name_normalized = display_name.lower().replace(' ', '').replace('.', '')
                print(f"Processing participant: '{display_name}'")
                
                # Check against enrolled students FIRST (priority)
                matched_student = None
                for student in scheduled_class.students:
                    if student.full_name:
                        student_name_normalized = student.full_name.lower().strip().replace(' ', '').replace('.', '')
                        # Check if student name is contained in display name
                        if student_name_normalized and student_name_normalized in display_name_normalized:
                            matched_student = student
                            print(f"✓ STUDENT match: '{display_name}' contains '{student.full_name}'")
                            break
                
                # If matched a student, assign as student
                if matched_student:
                    teacher_id = None
                    student_id = matched_student.id
                    role = UserRole.STUDENT
                # Otherwise check against teacher (not a student, so check if teacher)
                elif teacher and teacher.full_name:
                    teacher_name_normalized = teacher.full_name.lower().strip().replace(' ', '').replace('.', '')
                    # Check if teacher name is contained in display name
                    if teacher_name_normalized and teacher_name_normalized in display_name_normalized:
                        teacher_id = teacher.id
                        student_id = None
                        role = UserRole.TEACHER
                        print(f"✓ TEACHER match: '{display_name}' contains '{teacher.full_name}'")
                    else:
                        # Not teacher, not student - skip (shared account user)
                        print(f"⊘ No match: '{display_name}' - skipping")
                        continue
                else:
                    # No teacher found - skip
                    print(f"⊘ No match: '{display_name}' - skipping")
                    continue
                
                # Get session data (use first/earliest session if multiple)
                sessions = participant_data.get('sessions', [])
                if not sessions:
                    continue
                
                # Use the earliest start time and latest end time across all sessions
                join_time = min((s['start_time'] for s in sessions if s.get('start_time')), default=None)
                leave_time = max((s['end_time'] for s in sessions if s.get('end_time')), default=None)
                total_duration_seconds = participant_data.get('total_duration_seconds', 0)
                
                if email in existing_logs:
                    # Update existing log if new data is more complete
                    log = existing_logs[email]
                    
                    # Update display name if we have it and it's not set
                    if display_name and (not log.display_name or log.display_name == 'Unknown'):
                        log.display_name = display_name
                        print(f"Updated display name for {email}: {display_name}")
                    
                    # Update join time if we have it and it's earlier
                    if join_time and (not log.join_time or join_time < log.join_time):
                        log.join_time = join_time
                        print(f"Updated join time for {email}")
                    
                    # Update exit time if we have it
                    if leave_time and not log.exit_time:
                        log.exit_time = leave_time
                        if log.join_time:
                            duration = (log.exit_time - log.join_time).total_seconds() / 60
                            log.duration_minutes = round(duration, 2)
                        print(f"Updated exit time for {email}")
                else:
                    # Create new attendance log
                    if not join_time:
                        continue
                    
                    # Calculate duration
                    duration_minutes = None
                    if total_duration_seconds > 0:
                        duration_minutes = round(total_duration_seconds / 60, 2)
                    
                    # Create attendance log (role, teacher_id, student_id already set above)
                    attendance_log = AttendanceLog(
                        session_id=session.id,
                        user_email=email,
                        display_name=display_name,
                        role=role,
                        teacher_id=teacher_id,
                        student_id=student_id,
                        join_time=join_time,
                        exit_time=leave_time,
                        duration_minutes=duration_minutes
                    )
                    
                    db.add(attendance_log)
                    print(f"Created attendance log for {display_name} ({email}) - {role.value}")
            
            print(f"Synced participant data for session {session.id}")
            
        except Exception as e:
            print(f"Error syncing participant data for session {session.id}: {e}")
            import traceback
            traceback.print_exc()
            # Don't raise - we'll retry on next fetch
    
    async def retry_failed_fetches(self):
        """
        Retry fetching participant data for recently completed classes
        that have no attendance logs (indicating a failed fetch)
        """
        async with AsyncSessionLocal() as db:
            try:
                # Find completed classes from the last 7 days with no attendance logs
                seven_days_ago = datetime.utcnow() - timedelta(days=7)
                
                stmt = select(ScheduledClass).options(
                    selectinload(ScheduledClass.students)
                ).where(
                    ScheduledClass.is_completed == True,
                    ScheduledClass.end_time >= seven_days_ago,
                    ScheduledClass.google_meet_code.isnot(None),
                    ScheduledClass.session_id.isnot(None)
                )
                
                result = await db.execute(stmt)
                completed_classes = result.scalars().all()
                
                classes_to_retry = []
                for scheduled_class in completed_classes:
                    # Check if this session has any attendance logs
                    attendance_stmt = select(AttendanceLog).where(
                        AttendanceLog.session_id == scheduled_class.session_id
                    )
                    attendance_result = await db.execute(attendance_stmt)
                    logs = attendance_result.scalars().all()
                    
                    if not logs:
                        classes_to_retry.append(scheduled_class)
                
                if not classes_to_retry:
                    print("No failed fetches to retry")
                    return
                
                print(f"Retrying participant fetch for {len(classes_to_retry)} completed classes without attendance logs...")
                
                for scheduled_class in classes_to_retry:
                    # Get session
                    session_stmt = select(Session).where(Session.id == scheduled_class.session_id)
                    session_result = await db.execute(session_stmt)
                    session = session_result.scalars().first()
                    
                    if session:
                        print(f"Retrying fetch for class {scheduled_class.id} ({scheduled_class.google_meet_code})")
                        
                        # Reload the scheduled_class with students to avoid lazy loading
                        class_stmt = select(ScheduledClass).options(
                            selectinload(ScheduledClass.students)
                        ).where(ScheduledClass.id == scheduled_class.id)
                        class_result = await db.execute(class_stmt)
                        scheduled_class_with_students = class_result.scalars().first()
                        
                        if scheduled_class_with_students:
                            await self.sync_participant_data(db, session, scheduled_class_with_students)
                
                await db.commit()
                print("Retry fetch completed")
                
            except Exception as e:
                print(f"Error in retry_failed_fetches: {e}")
                await db.rollback()


# Global instance
_monitor_service = None


def get_monitor_service() -> MeetingMonitorService:
    """Get or create MeetingMonitorService singleton"""
    global _monitor_service
    if _monitor_service is None:
        _monitor_service = MeetingMonitorService()
    return _monitor_service


def start_monitoring():
    """Start the monitoring service"""
    service = get_monitor_service()
    service.start()


def stop_monitoring():
    """Stop the monitoring service"""
    service = get_monitor_service()
    service.stop()
