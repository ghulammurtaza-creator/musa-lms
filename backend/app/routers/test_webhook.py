"""
Test endpoint to manually simulate Google Meet join/leave events
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.services.duration_service import DurationCalculationEngine
from app.models.models import UserRole

router = APIRouter(prefix="/api/test", tags=["Testing"])


class TestJoinRequest(BaseModel):
    meeting_code: str
    user_email: str
    role: str  # "Teacher" or "Student"


class TestExitRequest(BaseModel):
    meeting_code: str
    user_email: str


@router.post("/join")
async def test_join(request: TestJoinRequest, db: AsyncSession = Depends(get_db)):
    """
    Manually simulate a user joining a Google Meet
    """
    # Convert role string to UserRole enum
    role = UserRole.TEACHER if request.role.lower() == "teacher" else UserRole.STUDENT
    
    # Use DurationCalculationEngine to process join
    await DurationCalculationEngine.process_join_event(
        db=db,
        session_id=None,  # Will be created if doesn't exist
        user_email=request.user_email,
        role=role,
        join_time=datetime.utcnow(),
        teacher_id=None,
        student_id=None
    )
    
    await db.commit()
    
    return {
        "status": "success",
        "message": f"{request.user_email} joined meeting {request.meeting_code}"
    }


@router.post("/exit")
async def test_exit(request: TestExitRequest, db: AsyncSession = Depends(get_db)):
    """
    Manually simulate a user leaving a Google Meet
    """
    # Use DurationCalculationEngine to process exit
    result = await DurationCalculationEngine.process_exit_event(
        db=db,
        session_id=None,  # Will find by user email
        user_email=request.user_email,
        exit_time=datetime.utcnow()
    )
    
    await db.commit()
    
    return {
        "status": "success",
        "message": f"{request.user_email} left meeting {request.meeting_code}",
        "duration_minutes": result.duration_minutes if result else None
    }

