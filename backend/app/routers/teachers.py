from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.models.models import Teacher
from app.schemas.schemas import TeacherCreate, TeacherUpdate, TeacherResponse

router = APIRouter(prefix="/teachers", tags=["Teachers"])


@router.post("/", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
async def create_teacher(
    teacher_data: TeacherCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new teacher"""
    # Check if email already exists
    stmt = select(Teacher).where(Teacher.email == teacher_data.email)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Teacher with email {teacher_data.email} already exists"
        )
    
    teacher = Teacher(**teacher_data.model_dump())
    db.add(teacher)
    await db.commit()
    await db.refresh(teacher)
    return teacher


@router.get("/", response_model=List[TeacherResponse])
async def get_all_teachers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all teachers"""
    stmt = select(Teacher).offset(skip).limit(limit)
    result = await db.execute(stmt)
    teachers = result.scalars().all()
    return teachers


@router.get("/{teacher_id}", response_model=TeacherResponse)
async def get_teacher(
    teacher_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific teacher by ID"""
    stmt = select(Teacher).where(Teacher.id == teacher_id)
    result = await db.execute(stmt)
    teacher = result.scalars().first()
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with id {teacher_id} not found"
        )
    
    return teacher


@router.patch("/{teacher_id}", response_model=TeacherResponse)
async def update_teacher(
    teacher_id: int,
    teacher_data: TeacherUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a teacher"""
    stmt = select(Teacher).where(Teacher.id == teacher_id)
    result = await db.execute(stmt)
    teacher = result.scalars().first()
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with id {teacher_id} not found"
        )
    
    # Update only provided fields
    update_data = teacher_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(teacher, field, value)
    
    await db.commit()
    await db.refresh(teacher)
    return teacher


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher(
    teacher_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a teacher"""
    stmt = select(Teacher).where(Teacher.id == teacher_id)
    result = await db.execute(stmt)
    teacher = result.scalars().first()
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with id {teacher_id} not found"
        )
    
    await db.delete(teacher)
    await db.commit()
    return None
