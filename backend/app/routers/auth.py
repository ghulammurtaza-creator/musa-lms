from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import timedelta

from app.core.database import get_db
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    require_admin,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.models.models import AuthUser, AuthUserRole
from app.schemas.schemas import (
    UserSignup,
    UserLogin,
    Token,
    AuthUserResponse,
    AuthUserWithRelations
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthUserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignup, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    result = await db.execute(select(AuthUser).filter(AuthUser.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = AuthUser(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role,
        hourly_rate=user_data.hourly_rate,
        is_active=True
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login and get access token"""
    # Find user by email (username field in OAuth2PasswordRequestForm)
    result = await db.execute(select(AuthUser).filter(AuthUser.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=AuthUserResponse)
async def get_current_user_info(current_user: AuthUser = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.get("/users", response_model=List[AuthUserResponse])
async def list_users(
    role: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(require_admin)
):
    """List all users (admin only)"""
    query = select(AuthUser)
    
    if role:
        try:
            role_enum = AuthUserRole(role)
            query = query.filter(AuthUser.role == role_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {role}"
            )
    
    result = await db.execute(query)
    users = result.scalars().all()
    return users


@router.get("/users/{user_id}", response_model=AuthUserWithRelations)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    """Get user details with relationships"""
    # Users can view their own info, admins can view anyone
    if current_user.id != user_id and current_user.role != AuthUserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )
    
    result = await db.execute(select(AuthUser).filter(AuthUser.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(require_admin)
):
    """Delete a user (admin only)"""
    result = await db.execute(select(AuthUser).filter(AuthUser.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await db.delete(user)
    await db.commit()
    return None


@router.get("/tutors", response_model=List[AuthUserResponse])
async def list_tutors(
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    """List all tutors (available to all authenticated users)"""
    result = await db.execute(select(AuthUser).filter(AuthUser.role == AuthUserRole.TUTOR))
    tutors = result.scalars().all()
    return tutors


@router.get("/students", response_model=List[AuthUserResponse])
async def list_students(
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    """List all students (available to tutors and admins)"""
    if current_user.role not in [AuthUserRole.ADMIN, AuthUserRole.TUTOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view students list"
        )
    
    result = await db.execute(select(AuthUser).filter(AuthUser.role == AuthUserRole.STUDENT))
    students = result.scalars().all()
    return students
