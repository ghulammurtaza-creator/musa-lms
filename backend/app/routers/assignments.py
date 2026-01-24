from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user, require_tutor
from app.services.minio_service import get_minio_service
from app.models.models import (
    AuthUser,
    AuthUserRole,
    Assignment,
    AssignmentSubmission,
    AssignmentStatus,
    student_tutor
)
from app.schemas.schemas import (
    AssignmentCreate,
    AssignmentUpdate,
    AssignmentResponse,
    AssignmentWithTutor,
    AssignmentSubmissionCreate,
    AssignmentSubmissionUpdate,
    AssignmentSubmissionGrade,
    AssignmentSubmissionResponse,
    AssignmentSubmissionWithDetails
)

router = APIRouter(prefix="/api/assignments", tags=["Assignments"])


@router.post("", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assignment_data: AssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(require_tutor)
):
    """Create a new assignment (tutor/admin only)"""
    # Verify all student IDs exist and are students
    result = await db.execute(
        select(AuthUser).filter(
            AuthUser.id.in_(assignment_data.student_ids),
            AuthUser.role == AuthUserRole.STUDENT
        )
    )
    students = result.scalars().all()
    
    if len(students) != len(assignment_data.student_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more invalid student IDs"
        )
    
    # Verify students are assigned to this tutor (if not admin)
    if current_user.role != AuthUserRole.ADMIN:
        # Reload current user with students relationship
        result = await db.execute(
            select(AuthUser)
            .options(selectinload(AuthUser.students))
            .filter(AuthUser.id == current_user.id)
        )
        tutor = result.scalar_one()
        assigned_student_ids = [s.id for s in tutor.students]
        
        for student_id in assignment_data.student_ids:
            if student_id not in assigned_student_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Student {student_id} is not assigned to you"
                )
    
    # Create assignment
    new_assignment = Assignment(
        tutor_id=current_user.id,
        title=assignment_data.title,
        description=assignment_data.description,
        due_date=assignment_data.due_date,
        total_points=assignment_data.total_points
    )
    
    db.add(new_assignment)
    await db.commit()
    await db.refresh(new_assignment)
    
    # Create submission records for each student
    for student_id in assignment_data.student_ids:
        submission = AssignmentSubmission(
            assignment_id=new_assignment.id,
            student_id=student_id,
            status=AssignmentStatus.PENDING
        )
        db.add(submission)
    
    await db.commit()
    
    return new_assignment


@router.get("", response_model=List[AssignmentWithTutor])
async def list_assignments(
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    """List assignments based on user role"""
    if current_user.role == AuthUserRole.STUDENT:
        # Get assignments assigned to this student
        result = await db.execute(
            select(AssignmentSubmission).filter(
                AssignmentSubmission.student_id == current_user.id
            )
        )
        submissions = result.scalars().all()
        assignment_ids = [s.assignment_id for s in submissions]
        
        result = await db.execute(
            select(Assignment).filter(Assignment.id.in_(assignment_ids))
        )
        assignments = result.scalars().all()
    elif current_user.role == AuthUserRole.TUTOR:
        # Get assignments created by this tutor
        result = await db.execute(
            select(Assignment).filter(Assignment.tutor_id == current_user.id)
        )
        assignments = result.scalars().all()
    else:  # ADMIN
        # Get all assignments
        result = await db.execute(select(Assignment))
        assignments = result.scalars().all()
    
    return assignments


@router.get("/my-submissions", response_model=List[AssignmentSubmissionWithDetails])
async def get_my_submissions(
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    """Get all submissions for the current student"""
    if current_user.role != AuthUserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can view their submissions"
        )
    
    try:
        result = await db.execute(
            select(AssignmentSubmission)
            .options(
                selectinload(AssignmentSubmission.assignment).selectinload(Assignment.tutor),
                selectinload(AssignmentSubmission.student)
            )
            .filter(AssignmentSubmission.student_id == current_user.id)
        )
        submissions = result.scalars().all()
        
        return submissions
    except Exception as e:
        print(f"Error in get_my_submissions: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


@router.get("/{assignment_id}", response_model=AssignmentWithTutor)
async def get_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    """Get assignment details"""
    result = await db.execute(
        select(Assignment).filter(Assignment.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Check authorization
    if current_user.role == AuthUserRole.STUDENT:
        # Check if student has this assignment
        result = await db.execute(
            select(AssignmentSubmission).filter(
                AssignmentSubmission.assignment_id == assignment_id,
                AssignmentSubmission.student_id == current_user.id
            )
        )
        submission = result.scalar_one_or_none()
        
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this assignment"
            )
    elif current_user.role == AuthUserRole.TUTOR:
        # Check if tutor owns this assignment
        if assignment.tutor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this assignment"
            )
    
    return assignment


@router.put("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: int,
    assignment_data: AssignmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(require_tutor)
):
    """Update an assignment (tutor/admin only)"""
    result = await db.execute(
        select(Assignment).filter(Assignment.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Check if tutor owns this assignment (unless admin)
    if current_user.role != AuthUserRole.ADMIN and assignment.tutor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this assignment"
        )
    
    # Update fields
    if assignment_data.title is not None:
        assignment.title = assignment_data.title
    if assignment_data.description is not None:
        assignment.description = assignment_data.description
    if assignment_data.due_date is not None:
        assignment.due_date = assignment_data.due_date
    if assignment_data.total_points is not None:
        assignment.total_points = assignment_data.total_points
    
    await db.commit()
    await db.refresh(assignment)
    
    return assignment


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(require_tutor)
):
    """Delete an assignment (tutor/admin only)"""
    result = await db.execute(
        select(Assignment).filter(Assignment.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Check if tutor owns this assignment (unless admin)
    if current_user.role != AuthUserRole.ADMIN and assignment.tutor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this assignment"
        )
    
    await db.delete(assignment)
    await db.commit()
    return None


# Submission routes
@router.get("/{assignment_id}/submissions", response_model=List[AssignmentSubmissionWithDetails])
async def list_submissions(
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    """List submissions for an assignment"""
    result = await db.execute(
        select(Assignment).filter(Assignment.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Check authorization
    if current_user.role == AuthUserRole.STUDENT:
        # Student can only see their own submission
        result = await db.execute(
            select(AssignmentSubmission)
            .options(
                selectinload(AssignmentSubmission.assignment).selectinload(Assignment.tutor),
                selectinload(AssignmentSubmission.student)
            )
            .filter(
                AssignmentSubmission.assignment_id == assignment_id,
                AssignmentSubmission.student_id == current_user.id
            )
        )
        submissions = result.scalars().all()
    elif current_user.role == AuthUserRole.TUTOR:
        # Tutor can see all submissions for their assignment
        if assignment.tutor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view these submissions"
            )
        result = await db.execute(
            select(AssignmentSubmission)
            .options(
                selectinload(AssignmentSubmission.assignment).selectinload(Assignment.tutor),
                selectinload(AssignmentSubmission.student)
            )
            .filter(AssignmentSubmission.assignment_id == assignment_id)
        )
        submissions = result.scalars().all()
    else:  # ADMIN
        # Admin can see all submissions
        result = await db.execute(
            select(AssignmentSubmission)
            .options(
                selectinload(AssignmentSubmission.assignment).selectinload(Assignment.tutor),
                selectinload(AssignmentSubmission.student)
            )
            .filter(AssignmentSubmission.assignment_id == assignment_id)
        )
        submissions = result.scalars().all()
    
    return submissions


@router.post("/{assignment_id}/submit", response_model=AssignmentSubmissionResponse)
async def submit_assignment(
    assignment_id: int,
    submission_text: Optional[str] = None,
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    """Submit an assignment (student only)"""
    if current_user.role != AuthUserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can submit assignments"
        )
    
    # Find the submission record
    result = await db.execute(
        select(AssignmentSubmission).filter(
            AssignmentSubmission.assignment_id == assignment_id,
            AssignmentSubmission.student_id == current_user.id
        )
    )
    submission = result.scalar_one_or_none()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found or not assigned to you"
        )
    
    # Handle file upload to MinIO
    if file:
        try:
            minio_service = get_minio_service()
            
            # Delete old file if exists
            if submission.file_path:
                minio_service.delete_file(submission.file_path)
            
            # Read file content
            file_content = await file.read()
            
            # Upload to MinIO
            object_name = minio_service.upload_file(
                file_data=file_content,
                file_name=file.filename,
                content_type=file.content_type or "application/octet-stream",
                folder=f"assignments/{assignment_id}/student_{current_user.id}"
            )
            
            submission.file_path = object_name
            
        except Exception as e:
            print(f"Error uploading file to MinIO: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file"
            )
    
    # Update submission
    submission.submission_text = submission_text
    submission.status = AssignmentStatus.SUBMITTED
    submission.submitted_at = datetime.now()
    
    await db.commit()
    await db.refresh(submission)
    
    return submission


@router.put("/submissions/{submission_id}/grade", response_model=AssignmentSubmissionResponse)
async def grade_submission(
    submission_id: int,
    grade_data: AssignmentSubmissionGrade,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(require_tutor)
):
    """Grade a submission (tutor/admin only)"""
    result = await db.execute(
        select(AssignmentSubmission).filter(AssignmentSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    # Check if tutor owns this assignment (unless admin)
    if current_user.role != AuthUserRole.ADMIN:
        result = await db.execute(
            select(Assignment).filter(Assignment.id == submission.assignment_id)
        )
        assignment = result.scalar_one_or_none()
        if assignment.tutor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to grade this submission"
            )
    
    # Validate grade
    result = await db.execute(
        select(Assignment).filter(Assignment.id == submission.assignment_id)
    )
    assignment = result.scalar_one_or_none()
    if grade_data.grade > assignment.total_points:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Grade cannot exceed {assignment.total_points} points"
        )
    
    # Update submission
    submission.grade = grade_data.grade
    submission.feedback = grade_data.feedback
    submission.status = AssignmentStatus.GRADED
    submission.graded_at = datetime.now()
    
    await db.commit()
    await db.refresh(submission)
    
    return submission


@router.get("/submissions/{submission_id}/download")
async def download_submission_file(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    """Download a submission file (tutor/admin or the student who submitted)"""
    # Get submission
    result = await db.execute(
        select(AssignmentSubmission)
        .options(selectinload(AssignmentSubmission.assignment))
        .filter(AssignmentSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    # Check authorization
    if current_user.role == AuthUserRole.STUDENT:
        if submission.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to download this file"
            )
    elif current_user.role == AuthUserRole.TUTOR:
        if submission.assignment.tutor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to download this file"
            )
    
    # Check if file exists
    if not submission.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No file attached to this submission"
        )
    
    try:
        minio_service = get_minio_service()
        file_data = minio_service.download_file(submission.file_path)
        
        # Extract filename from object path
        filename = submission.file_path.split('/')[-1]
        
        # Determine content type based on file extension
        import mimetypes
        content_type, _ = mimetypes.guess_type(filename)
        if not content_type:
            content_type = "application/octet-stream"
        
        return Response(
            content=file_data,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        print(f"Error downloading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download file"
        )


@router.get("/submissions/{submission_id}/file-url")
async def get_submission_file_url(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    """Get a presigned URL for downloading a submission file"""
    # Get submission
    result = await db.execute(
        select(AssignmentSubmission)
        .options(selectinload(AssignmentSubmission.assignment))
        .filter(AssignmentSubmission.id == submission_id)
    )
    submission = result.scalar_one_or_none()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    # Check authorization
    if current_user.role == AuthUserRole.STUDENT:
        if submission.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this file"
            )
    elif current_user.role == AuthUserRole.TUTOR:
        if submission.assignment.tutor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this file"
            )
    
    # Check if file exists
    if not submission.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No file attached to this submission"
        )
    
    try:
        minio_service = get_minio_service()
        presigned_url = minio_service.get_presigned_url(
            submission.file_path,
            expires=timedelta(hours=1)
        )
        
        return {
            "url": presigned_url,
            "expires_in": 3600,  # seconds
            "filename": submission.file_path.split('/')[-1]
        }
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate download URL"
        )
