from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.models.models import Family
from app.schemas.schemas import FamilyCreate, FamilyUpdate, FamilyResponse

router = APIRouter(prefix="/families", tags=["Families"])


@router.post("/", response_model=FamilyResponse, status_code=status.HTTP_201_CREATED)
async def create_family(
    family_data: FamilyCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new family"""
    # Check if family_number already exists
    stmt = select(Family).where(Family.family_number == family_data.family_number)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Family number {family_data.family_number} already exists"
        )
    
    family = Family(**family_data.model_dump())
    db.add(family)
    await db.commit()
    await db.refresh(family)
    return family


@router.get("/", response_model=List[FamilyResponse])
async def get_all_families(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all families"""
    stmt = select(Family).offset(skip).limit(limit)
    result = await db.execute(stmt)
    families = result.scalars().all()
    return families


@router.get("/{family_id}", response_model=FamilyResponse)
async def get_family(
    family_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific family by ID"""
    stmt = select(Family).where(Family.id == family_id)
    result = await db.execute(stmt)
    family = result.scalars().first()
    
    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Family with id {family_id} not found"
        )
    
    return family


@router.patch("/{family_id}", response_model=FamilyResponse)
async def update_family(
    family_id: int,
    family_data: FamilyUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a family"""
    stmt = select(Family).where(Family.id == family_id)
    result = await db.execute(stmt)
    family = result.scalars().first()
    
    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Family with id {family_id} not found"
        )
    
    # Update only provided fields
    update_data = family_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(family, field, value)
    
    await db.commit()
    await db.refresh(family)
    return family


@router.delete("/{family_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_family(
    family_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a family"""
    stmt = select(Family).where(Family.id == family_id)
    result = await db.execute(stmt)
    family = result.scalars().first()
    
    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Family with id {family_id} not found"
        )
    
    await db.delete(family)
    await db.commit()
    return None
