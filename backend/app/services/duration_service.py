from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.models.models import AttendanceLog, Session, AuthUser, AuthUserRole, UserRole


class DurationCalculationEngine:
    """
    Handles complex duration calculations for attendance logs.
    Stitches multiple join/exit events for a single user in one session.
    """
    
    @staticmethod
    async def process_join_event(
        db: AsyncSession,
        session_id: int,
        user_email: str,
        role: UserRole,
        join_time: datetime,
        teacher_id: Optional[int] = None,
        student_id: Optional[int] = None
    ) -> AttendanceLog:
        """
        Process a join event. Creates a new attendance log entry.
        """
        attendance_log = AttendanceLog(
            session_id=session_id,
            user_email=user_email,
            role=role,  # Pass the enum directly, SQLAlchemy will handle it
            teacher_id=teacher_id,
            student_id=student_id,
            join_time=join_time,
            exit_time=None,
            duration_minutes=0.0
        )
        db.add(attendance_log)
        await db.commit()
        await db.refresh(attendance_log)
        return attendance_log
    
    @staticmethod
    async def process_exit_event(
        db: AsyncSession,
        session_id: int,
        user_email: str,
        exit_time: datetime
    ) -> Optional[AttendanceLog]:
        """
        Process an exit event. Finds the most recent join without an exit
        and calculates the duration.
        """
        # Find the most recent join event for this user in this session without an exit time
        stmt = select(AttendanceLog).where(
            and_(
                AttendanceLog.session_id == session_id,
                AttendanceLog.user_email == user_email,
                AttendanceLog.exit_time.is_(None)
            )
        ).order_by(AttendanceLog.join_time.desc())
        
        result = await db.execute(stmt)
        attendance_log = result.scalars().first()
        
        if attendance_log:
            # Calculate duration in minutes
            duration = (exit_time - attendance_log.join_time).total_seconds() / 60
            attendance_log.exit_time = exit_time
            attendance_log.duration_minutes = max(0, duration)  # Ensure non-negative
            
            await db.commit()
            await db.refresh(attendance_log)
            return attendance_log
        
        return None
    
    @staticmethod
    async def stitch_overlapping_sessions(
        db: AsyncSession,
        session_id: int,
        user_email: str,
        max_gap_minutes: int = 5
    ) -> float:
        """
        Stitch multiple join/exit events for a user, handling disconnections.
        If the gap between exit and next join is <= max_gap_minutes, treat as continuous.
        Returns total stitched duration in minutes.
        """
        # Get all attendance logs for this user in this session, ordered by join time
        stmt = select(AttendanceLog).where(
            and_(
                AttendanceLog.session_id == session_id,
                AttendanceLog.user_email == user_email
            )
        ).order_by(AttendanceLog.join_time.asc())
        
        result = await db.execute(stmt)
        logs = result.scalars().all()
        
        if not logs:
            return 0.0
        
        total_duration = 0.0
        segments = []
        
        for log in logs:
            if log.exit_time:
                segments.append({
                    'start': log.join_time,
                    'end': log.exit_time,
                    'duration': log.duration_minutes
                })
        
        if not segments:
            return 0.0
        
        # Merge overlapping or close segments
        merged_segments = []
        current_segment = segments[0]
        
        for next_segment in segments[1:]:
            gap = (next_segment['start'] - current_segment['end']).total_seconds() / 60
            
            if gap <= max_gap_minutes:
                # Merge segments
                current_segment['end'] = next_segment['end']
            else:
                # Save current segment and start a new one
                merged_segments.append(current_segment)
                current_segment = next_segment
        
        # Add the last segment
        merged_segments.append(current_segment)
        
        # Calculate total duration from merged segments
        for segment in merged_segments:
            duration = (segment['end'] - segment['start']).total_seconds() / 60
            total_duration += duration
        
        return total_duration
    
    @staticmethod
    async def calculate_student_monthly_duration(
        db: AsyncSession,
        student_id: int,
        year: int,
        month: int
    ) -> float:
        """
        Calculate total duration for a student in a specific month.
        """
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        stmt = select(func.sum(AttendanceLog.duration_minutes)).where(
            and_(
                AttendanceLog.student_id == student_id,
                AttendanceLog.join_time >= start_date,
                AttendanceLog.join_time < end_date
            )
        )
        
        result = await db.execute(stmt)
        total_minutes = result.scalar() or 0.0
        return total_minutes
    
    @staticmethod
    async def calculate_teacher_monthly_duration(
        db: AsyncSession,
        teacher_id: int,
        year: int,
        month: int
    ) -> float:
        """
        Calculate total duration for a teacher in a specific month.
        """
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        stmt = select(func.sum(AttendanceLog.duration_minutes)).where(
            and_(
                AttendanceLog.teacher_id == teacher_id,
                AttendanceLog.join_time >= start_date,
                AttendanceLog.join_time < end_date
            )
        )
        
        result = await db.execute(stmt)
        total_minutes = result.scalar() or 0.0
        return total_minutes
    
    @staticmethod
    async def get_active_sessions(db: AsyncSession) -> List[Dict]:
        """
        Get all currently active sessions (sessions without end_time).
        """
        stmt = select(Session).where(Session.end_time.is_(None)).order_by(Session.start_time.desc())
        
        result = await db.execute(stmt)
        sessions = result.scalars().all()
        
        active_sessions = []
        for session in sessions:
            # Get all attendance logs for this session
            logs_stmt = select(AttendanceLog).where(
                AttendanceLog.session_id == session.id
            ).order_by(AttendanceLog.join_time.desc())
            
            logs_result = await db.execute(logs_stmt)
            logs = logs_result.scalars().all()
            
            # Get teacher info
            teacher_stmt = select(AuthUser).where(AuthUser.id == session.teacher_id)
            teacher_result = await db.execute(teacher_stmt)
            teacher = teacher_result.scalars().first()
            
            participants = []
            for log in logs:
                participants.append({
                    'user_email': log.user_email,
                    'role': log.role,
                    'join_time': log.join_time,
                    'is_active': log.exit_time is None
                })
            
            active_sessions.append({
                'session_id': session.id,
                'meeting_id': session.meeting_id,
                'teacher_name': teacher.full_name if teacher else 'Unknown',
                'start_time': session.start_time,
                'participants': participants
            })
        
        return active_sessions
