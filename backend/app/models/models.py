from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy import Boolean, JSON, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    TEACHER = "Teacher"
    STUDENT = "Student"


class AuthUserRole(str, enum.Enum):
    ADMIN = "admin"
    TUTOR = "tutor"
    STUDENT = "student"


class AssignmentStatus(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    GRADED = "graded"


class Family(Base):
    """Family model to group students for billing purposes"""
    __tablename__ = "families"
    
    id = Column(Integer, primary_key=True, index=True)
    family_number = Column(String(50), unique=True, nullable=False, index=True)
    parent_name = Column(String(255), nullable=False)
    parent_email = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    students = relationship("Student", back_populates="family", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Family {self.family_number}: {self.parent_name}>"


class Student(Base):
    """Student model with family relationship (DEPRECATED - use AuthUser instead)"""
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    family_id = Column(Integer, ForeignKey("families.id", ondelete="CASCADE"), nullable=False)
    hourly_rate = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    family = relationship("Family", back_populates="students")
    # attendance_logs relationship removed - migrated to AuthUser
    
    def __repr__(self):
        return f"<Student {self.name} ({self.email})>"


class Teacher(Base):
    """Teacher model with subject specialties (DEPRECATED - use AuthUser instead)"""
    __tablename__ = "teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hourly_rate = Column(Float, nullable=False, default=0.0)
    subject_specialties = Column(Text)  # JSON or comma-separated
    google_credentials = Column(Text)  # JSON string of OAuth credentials
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Teacher {self.name} ({self.email})>"


class Session(Base):
    """Session (meeting) model"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(String(255), unique=True, nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey("auth_users.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))
    ai_summary = Column(Text)
    is_scheduled = Column(Boolean, default=False)  # New: indicates if scheduled via platform
    google_meet_code = Column(String(255))  # New: Google Meet code
    google_calendar_event_id = Column(String(255))  # New: Calendar event ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    teacher = relationship("AuthUser", foreign_keys=[teacher_id], backref="sessions")
    attendance_logs = relationship("AttendanceLog", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Session {self.meeting_id} - Teacher: {self.teacher_id}>"


class AttendanceLog(Base):
    """Attendance log for tracking join/exit events"""
    __tablename__ = "attendance_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    user_email = Column(String(255), nullable=False, index=True)  # Can be email or Google user ID
    display_name = Column(String(255), nullable=True)  # Display name from Google Meet
    role = Column(SQLEnum(UserRole, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    
    # Foreign keys for both Teacher and Student (one will be null) - now points to auth_users
    teacher_id = Column(Integer, ForeignKey("auth_users.id", ondelete="CASCADE"), nullable=True)
    student_id = Column(Integer, ForeignKey("auth_users.id", ondelete="CASCADE"), nullable=True)
    
    join_time = Column(DateTime(timezone=True), nullable=False)
    exit_time = Column(DateTime(timezone=True))
    duration_minutes = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="attendance_logs")
    teacher = relationship("AuthUser", foreign_keys=[teacher_id])
    student = relationship("AuthUser", foreign_keys=[student_id])
    
    def __repr__(self):
        return f"<AttendanceLog {self.user_email} - {self.role}: {self.duration_minutes}min>"


# Association table for many-to-many relationship between ScheduledClass and Students
scheduled_class_students = Table(
    'scheduled_class_students',
    Base.metadata,
    Column('scheduled_class_id', Integer, ForeignKey('scheduled_classes.id', ondelete='CASCADE'), primary_key=True),
    Column('student_id', Integer, ForeignKey('auth_users.id', ondelete='CASCADE'), primary_key=True)
)


class ScheduledClass(Base):
    """Scheduled class model with Google Calendar/Meet integration"""
    __tablename__ = "scheduled_classes"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("auth_users.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String(255), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    
    # Google Calendar/Meet integration
    google_calendar_event_id = Column(String(255), unique=True)
    google_meet_link = Column(String(500))
    google_meet_code = Column(String(255))
    
    # Session tracking
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    teacher = relationship("AuthUser", foreign_keys=[teacher_id], backref="taught_classes")
    session = relationship("Session", backref="scheduled_class")
    students = relationship("AuthUser", secondary=scheduled_class_students, backref="enrolled_classes")
    
    def __repr__(self):
        return f"<ScheduledClass {self.subject} - {self.start_time}>"


# Association table for many-to-many relationship between Students and Tutors
student_tutor = Table(
    'student_tutor',
    Base.metadata,
    Column('student_id', Integer, ForeignKey('auth_users.id', ondelete='CASCADE'), primary_key=True),
    Column('tutor_id', Integer, ForeignKey('auth_users.id', ondelete='CASCADE'), primary_key=True),
    Column('assigned_at', DateTime(timezone=True), server_default=func.now())
)


class AuthUser(Base):
    """Authentication user model with role-based access"""
    __tablename__ = "auth_users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(SQLEnum(AuthUserRole, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    is_active = Column(Boolean, default=True)
    hourly_rate = Column(Float, nullable=False, default=50.0)  # Hourly rate for billing/payroll
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    google_credentials = Column(Text, nullable=True)  # JSON string of Google OAuth credentials
    
    # Relationships
    created_assignments = relationship("Assignment", back_populates="tutor", foreign_keys="Assignment.tutor_id")
    assignment_submissions = relationship("AssignmentSubmission", back_populates="student", foreign_keys="AssignmentSubmission.student_id")
    
    # Many-to-many relationship for students and tutors
    tutors = relationship(
        "AuthUser",
        secondary=student_tutor,
        primaryjoin=id == student_tutor.c.student_id,
        secondaryjoin=id == student_tutor.c.tutor_id,
        backref="students"
    )
    
    def __repr__(self):
        return f"<AuthUser {self.email} - {self.role}>"


class Assignment(Base):
    """Assignment model created by tutors"""
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    tutor_id = Column(Integer, ForeignKey("auth_users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)
    total_points = Column(Integer, default=100)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tutor = relationship("AuthUser", back_populates="created_assignments", foreign_keys=[tutor_id])
    submissions = relationship("AssignmentSubmission", back_populates="assignment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Assignment {self.title}>"


class AssignmentSubmission(Base):
    """Assignment submission model"""
    __tablename__ = "assignment_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("auth_users.id", ondelete="CASCADE"), nullable=False)
    submission_text = Column(Text)
    file_path = Column(String(500))  # Path to uploaded file
    status = Column(SQLEnum(AssignmentStatus, values_callable=lambda obj: [e.value for e in obj]), default=AssignmentStatus.PENDING)
    grade = Column(Integer)  # Grade out of total_points
    feedback = Column(Text)
    submitted_at = Column(DateTime(timezone=True))
    graded_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("AuthUser", back_populates="assignment_submissions", foreign_keys=[student_id])
    
    def __repr__(self):
        return f"<AssignmentSubmission Assignment:{self.assignment_id} Student:{self.student_id} - {self.status}>"
