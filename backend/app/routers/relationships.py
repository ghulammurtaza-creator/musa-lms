from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.models import AuthUser, AuthUserRole, student_tutor
from app.schemas.schemas import AuthUserResponse, AuthUserWithRelations, StudentTutorAssignment

router = APIRouter(prefix="/api/relationships", tags=["Student-Tutor Relationships"])


@router.post("/assign", status_code=status.HTTP_201_CREATED)
async def assign_student_to_tutor(
    assignment: StudentTutorAssignment,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(require_admin)
):
    """Assign a student to a tutor (admin only)"""
    # Verify student exists and is a student
    result = await db.execute(
        select(AuthUser)
        .options(selectinload(AuthUser.tutors))
        .filter(AuthUser.id == assignment.student_id, AuthUser.role == AuthUserRole.STUDENT)
    )
    student = result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Verify tutor exists and is a tutor
    result = await db.execute(
        select(AuthUser).filter(AuthUser.id == assignment.tutor_id, AuthUser.role == AuthUserRole.TUTOR)
    )
    tutor = result.scalar_one_or_none()
    
    if not tutor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutor not found"
        )
    
    # Check if already assigned
    if tutor in student.tutors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student is already assigned to this tutor"
        )
    
    # Create assignment
    student.tutors.append(tutor)
    await db.commit()
    
    return {"message": "Student successfully assigned to tutor"}


@router.delete("/unassign", status_code=status.HTTP_204_NO_CONTENT)
async def unassign_student_from_tutor(
    assignment: StudentTutorAssignment,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(require_admin)
):
    """Unassign a student from a tutor (admin only)"""
    # Verify student exists
    result = await db.execute(
        select(AuthUser)
        .options(selectinload(AuthUser.tutors))
        .filter(AuthUser.id == assignment.student_id, AuthUser.role == AuthUserRole.STUDENT)
    )
    student = result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Verify tutor exists
    result = await db.execute(
        select(AuthUser).filter(AuthUser.id == assignment.tutor_id, AuthUser.role == AuthUserRole.TUTOR)
    )
    tutor = result.scalar_one_or_none()
    
    if not tutor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutor not found"
        )
    
    # Check if assigned
    if tutor not in student.tutors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student is not assigned to this tutor"
        )
    
    # Remove assignment
    student.tutors.remove(tutor)
    await db.commit()
    
    return None


@router.get("/student/{student_id}/tutors", response_model=List[AuthUserResponse])
async def get_student_tutors(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    """Get all tutors for a student"""
    # Students can only view their own tutors, tutors and admins can view any
    if current_user.role == AuthUserRole.STUDENT and current_user.id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this student's tutors"
        )
    
    result = await db.execute(
        select(AuthUser)
        .options(selectinload(AuthUser.tutors))
        .filter(AuthUser.id == student_id, AuthUser.role == AuthUserRole.STUDENT)
    )
    student = result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    return student.tutors


@router.get("/tutor/{tutor_id}/students", response_model=List[AuthUserResponse])
async def get_tutor_students(
    tutor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    """Get all students for a tutor"""
    # Tutors can only view their own students, admins can view any
    if current_user.role == AuthUserRole.TUTOR and current_user.id != tutor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this tutor's students"
        )
    
    if current_user.role == AuthUserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students cannot view tutor's student lists"
        )
    
    result = await db.execute(
        select(AuthUser)
        .options(selectinload(AuthUser.students))
        .filter(AuthUser.id == tutor_id, AuthUser.role == AuthUserRole.TUTOR)
    )
    tutor = result.scalar_one_or_none()
    
    if not tutor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutor not found"
        )
    
    return tutor.students


@router.get("/my-tutors", response_model=List[AuthUserResponse])
async def get_my_tutors(
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    """Get tutors for the current student"""
    if current_user.role != AuthUserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )
    
    # Reload student with tutors relationship
    result = await db.execute(
        select(AuthUser)
        .options(selectinload(AuthUser.tutors))
        .filter(AuthUser.id == current_user.id)
    )
    student = result.scalar_one()
    return student.tutors


@router.get("/my-students", response_model=List[AuthUserResponse])
async def get_my_students(
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    """Get students for the current tutor"""
    if current_user.role not in [AuthUserRole.TUTOR, AuthUserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tutors and admins can access this endpoint"
        )
    
    if current_user.role == AuthUserRole.ADMIN:
        # Admin sees all students
        result = await db.execute(select(AuthUser).filter(AuthUser.role == AuthUserRole.STUDENT))
        students = result.scalars().all()
        return students
    
    # Reload tutor with students relationship
    result = await db.execute(
        select(AuthUser)
        .options(selectinload(AuthUser.students))
        .filter(AuthUser.id == current_user.id)
    )
    tutor = result.scalar_one()
    return tutor.students
