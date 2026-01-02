from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    TEACHER = "Teacher"
    STUDENT = "Student"


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
    """Student model with family relationship"""
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
    attendance_logs = relationship("AttendanceLog", back_populates="student", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Student {self.name} ({self.email})>"


class Teacher(Base):
    """Teacher model with subject specialties"""
    __tablename__ = "teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hourly_rate = Column(Float, nullable=False, default=0.0)
    subject_specialties = Column(Text)  # JSON or comma-separated
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sessions = relationship("Session", back_populates="teacher", cascade="all, delete-orphan")
    attendance_logs = relationship("AttendanceLog", back_populates="teacher", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Teacher {self.name} ({self.email})>"


class Session(Base):
    """Session (meeting) model"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(String(255), unique=True, nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))
    ai_summary = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    teacher = relationship("Teacher", back_populates="sessions")
    attendance_logs = relationship("AttendanceLog", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Session {self.meeting_id} - Teacher: {self.teacher_id}>"


class AttendanceLog(Base):
    """Attendance log for tracking join/exit events"""
    __tablename__ = "attendance_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    user_email = Column(String(255), nullable=False, index=True)
    role = Column(SQLEnum(UserRole, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    
    # Foreign keys for both Teacher and Student (one will be null)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=True)
    
    join_time = Column(DateTime(timezone=True), nullable=False)
    exit_time = Column(DateTime(timezone=True))
    duration_minutes = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="attendance_logs")
    teacher = relationship("Teacher", back_populates="attendance_logs")
    student = relationship("Student", back_populates="attendance_logs")
    
    def __repr__(self):
        return f"<AttendanceLog {self.user_email} - {self.role}: {self.duration_minutes}min>"
