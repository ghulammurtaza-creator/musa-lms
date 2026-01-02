from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.models.models import Student, Family
from app.schemas.schemas import StudentCreate, StudentUpdate, StudentResponse

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    student_data: StudentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new student"""
    # Check if email already exists
    stmt = select(Student).where(Student.email == student_data.email)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student with email {student_data.email} already exists"
        )
    
    # Verify family exists
    family_stmt = select(Family).where(Family.id == student_data.family_id)
    family_result = await db.execute(family_stmt)
    if not family_result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Family with id {student_data.family_id} not found"
        )
    
    student = Student(**student_data.model_dump())
    db.add(student)
    await db.commit()
    await db.refresh(student)
    return student


@router.get("/", response_model=List[StudentResponse])
async def get_all_students(
    skip: int = 0,
    limit: int = 100,
    family_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all students, optionally filtered by family"""
    if family_id:
        stmt = select(Student).where(Student.family_id == family_id).offset(skip).limit(limit)
    else:
        stmt = select(Student).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    students = result.scalars().all()
    return students


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific student by ID"""
    stmt = select(Student).where(Student.id == student_id)
    result = await db.execute(stmt)
    student = result.scalars().first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found"
        )
    
    return student


@router.patch("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a student"""
    stmt = select(Student).where(Student.id == student_id)
    result = await db.execute(stmt)
    student = result.scalars().first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found"
        )
    
    # Update only provided fields
    update_data = student_data.model_dump(exclude_unset=True)
    
    # Verify family exists if family_id is being updated
    if 'family_id' in update_data:
        family_stmt = select(Family).where(Family.id == update_data['family_id'])
        family_result = await db.execute(family_stmt)
        if not family_result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Family with id {update_data['family_id']} not found"
            )
    
    for field, value in update_data.items():
        setattr(student, field, value)
    
    await db.commit()
    await db.refresh(student)
    return student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a student"""
    stmt = select(Student).where(Student.id == student_id)
    result = await db.execute(stmt)
    student = result.scalars().first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found"
        )
    
    await db.delete(student)
    await db.commit()
    return None
