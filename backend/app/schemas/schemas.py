from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from app.models.models import UserRole


# Family Schemas
class FamilyBase(BaseModel):
    family_number: str = Field(..., min_length=1, max_length=50)
    parent_name: str = Field(..., min_length=1, max_length=255)
    parent_email: EmailStr


class FamilyCreate(FamilyBase):
    pass


class FamilyUpdate(BaseModel):
    parent_name: Optional[str] = Field(None, min_length=1, max_length=255)
    parent_email: Optional[EmailStr] = None


class FamilyResponse(FamilyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Student Schemas
class StudentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    hourly_rate: float = Field(..., ge=0)


class StudentCreate(StudentBase):
    family_id: int


class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    family_id: Optional[int] = None
    hourly_rate: Optional[float] = Field(None, ge=0)


class StudentResponse(StudentBase):
    id: int
    family_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Teacher Schemas
class TeacherBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    hourly_rate: float = Field(..., ge=0)
    subject_specialties: Optional[str] = None


class TeacherCreate(TeacherBase):
    pass


class TeacherUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    hourly_rate: Optional[float] = Field(None, ge=0)
    subject_specialties: Optional[str] = None


class TeacherResponse(TeacherBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Session Schemas
class SessionBase(BaseModel):
    meeting_id: str = Field(..., min_length=1, max_length=255)
    teacher_id: int
    start_time: datetime


class SessionCreate(SessionBase):
    pass


class SessionUpdate(BaseModel):
    end_time: Optional[datetime] = None
    ai_summary: Optional[str] = None


class SessionResponse(SessionBase):
    id: int
    end_time: Optional[datetime] = None
    ai_summary: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Attendance Log Schemas
class AttendanceLogBase(BaseModel):
    session_id: int
    user_email: str  # Can be email or Google user ID (users/xxxxx)
    display_name: Optional[str] = None  # Display name from Google Meet
    role: UserRole
    join_time: datetime


class AttendanceLogCreate(AttendanceLogBase):
    teacher_id: Optional[int] = None
    student_id: Optional[int] = None


class AttendanceLogUpdate(BaseModel):
    exit_time: Optional[datetime] = None
    duration_minutes: Optional[float] = Field(None, ge=0)


class AttendanceLogResponse(AttendanceLogBase):
    id: int
    teacher_id: Optional[int] = None
    student_id: Optional[int] = None
    exit_time: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Webhook Schemas
class GoogleMeetEvent(BaseModel):
    meeting_id: str
    user_email: EmailStr
    event_type: str  # "join" or "exit"
    timestamp: datetime
    role: UserRole


# Scheduled Class Schemas
class ScheduledClassCreate(BaseModel):
    teacher_email: EmailStr
    student_emails: List[EmailStr]
    subject: str = Field(..., min_length=1, max_length=255)
    start_time: datetime
    duration_minutes: int = Field(..., gt=0, le=480)  # Max 8 hours
    description: Optional[str] = None


class ScheduledClassUpdate(BaseModel):
    start_time: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, gt=0, le=480)
    student_emails: Optional[List[EmailStr]] = None


class ScheduledClassResponse(BaseModel):
    id: int
    teacher_id: int
    subject: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    google_meet_link: Optional[str] = None
    google_meet_code: Optional[str] = None
    is_active: bool
    is_completed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ScheduledClassWithDetails(ScheduledClassResponse):
    teacher: "TeacherResponse"
    students: List["StudentResponse"]
    session: Optional["SessionResponse"] = None
    
    class Config:
        from_attributes = True


# Billing Schemas
class StudentBillingItem(BaseModel):
    student_id: int
    student_name: str
    student_email: str
    total_minutes: float
    hourly_rate: float
    total_amount: float


class FamilyBilling(BaseModel):
    family_id: int
    family_number: str
    parent_name: str
    parent_email: str
    students: List[StudentBillingItem]
    total_family_amount: float
    billing_month: str


class TeacherPayroll(BaseModel):
    teacher_id: int
    teacher_name: str
    teacher_email: str
    total_minutes: float
    hourly_rate: float
    total_amount: float
    billing_month: str


# Real-time Monitoring Schemas
class ActiveSessionParticipant(BaseModel):
    user_email: str
    role: UserRole
    join_time: datetime
    is_active: bool


class ActiveSessionResponse(BaseModel):
    session_id: int
    meeting_id: str
    teacher_name: str
    start_time: datetime
    participants: List[ActiveSessionParticipant]
