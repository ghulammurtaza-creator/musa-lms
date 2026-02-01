from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime
from typing import List
from app.models.models import AuthUser, AuthUserRole, AttendanceLog
from app.schemas.schemas import FamilyBilling, StudentBillingItem, TeacherPayroll, StudentPayrollItem


class BillingService:
    """Service for handling student billing and teacher payroll calculations using AuthUser model"""
    
    @staticmethod
    async def calculate_student_billing(
        db: AsyncSession,
        student_id: int,
        year: int,
        month: int
    ) -> StudentBillingItem:
        """
        Calculate billing for a specific student for a given month.
        Uses AuthUser model instead of deprecated Student model.
        """
        # Get student details from AuthUser
        student_stmt = select(AuthUser).where(
            AuthUser.id == student_id,
            AuthUser.role == AuthUserRole.STUDENT
        )
        student_result = await db.execute(student_stmt)
        student = student_result.scalars().first()
        
        if not student:
            raise ValueError(f"Student with id {student_id} not found")
        
        # Calculate total duration for this student
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Query attendance logs for this student (student_id references auth_users.id)
        duration_stmt = select(func.sum(AttendanceLog.duration_minutes)).where(
            and_(
                AttendanceLog.student_id == student_id,
                AttendanceLog.join_time >= start_date,
                AttendanceLog.join_time < end_date
            )
        )
        
        result = await db.execute(duration_stmt)
        total_minutes = result.scalar() or 0.0
        
        # Calculate billing amount (convert minutes to hours)
        total_hours = total_minutes / 60
        total_amount = total_hours * student.hourly_rate
        
        return StudentBillingItem(
            student_id=student.id,
            student_name=student.full_name,
            student_email=student.email,
            total_minutes=total_minutes,
            hourly_rate=student.hourly_rate,
            total_amount=round(total_amount, 2)
        )
    
    @staticmethod
    async def calculate_all_families_billing(
        db: AsyncSession,
        year: int,
        month: int
    ) -> List[FamilyBilling]:
        """
        Calculate billing for all students grouped as "families" for a given month.
        Since we now use AuthUser, each student is treated as their own "family" unit.
        Returns students with activity during the month.
        """
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Get all students with attendance logs in the given month
        students_stmt = select(AuthUser).where(
            AuthUser.role == AuthUserRole.STUDENT,
            AuthUser.is_active == True
        )
        students_result = await db.execute(students_stmt)
        students = students_result.scalars().all()
        
        all_billings = []
        
        for student in students:
            try:
                # Calculate total duration for this student
                duration_stmt = select(func.sum(AttendanceLog.duration_minutes)).where(
                    and_(
                        AttendanceLog.student_id == student.id,
                        AttendanceLog.join_time >= start_date,
                        AttendanceLog.join_time < end_date
                    )
                )
                
                result = await db.execute(duration_stmt)
                total_minutes = result.scalar() or 0.0
                
                if total_minutes > 0:
                    total_hours = total_minutes / 60
                    total_amount = total_hours * student.hourly_rate
                    
                    student_billing = StudentBillingItem(
                        student_id=student.id,
                        student_name=student.full_name,
                        student_email=student.email,
                        total_minutes=total_minutes,
                        hourly_rate=student.hourly_rate,
                        total_amount=round(total_amount, 2)
                    )
                    
                    billing_month = f"{year}-{month:02d}"
                    
                    # Create a family billing entry for each student
                    # Using student email as parent email since we don't have family grouping
                    family_billing = FamilyBilling(
                        family_id=student.id,  # Use student ID as family ID
                        family_number=f"STU-{student.id:04d}",  # Generate family number
                        parent_name=student.full_name,  # Use student name
                        parent_email=student.email,
                        students=[student_billing],
                        total_family_amount=round(total_amount, 2),
                        billing_month=billing_month
                    )
                    
                    all_billings.append(family_billing)
            except Exception as e:
                print(f"Error calculating billing for student {student.id}: {e}")
                continue
        
        return all_billings
    
    @staticmethod
    async def calculate_family_billing(
        db: AsyncSession,
        family_id: int,
        year: int,
        month: int
    ) -> FamilyBilling:
        """
        Calculate billing for a specific student (treated as family unit).
        family_id now refers to auth_user.id for the student.
        """
        # Get student details from AuthUser
        student_stmt = select(AuthUser).where(AuthUser.id == family_id)
        student_result = await db.execute(student_stmt)
        student = student_result.scalars().first()
        
        if not student:
            raise ValueError(f"Student/Family with id {family_id} not found")
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Calculate total duration
        duration_stmt = select(func.sum(AttendanceLog.duration_minutes)).where(
            and_(
                AttendanceLog.student_id == student.id,
                AttendanceLog.join_time >= start_date,
                AttendanceLog.join_time < end_date
            )
        )
        
        result = await db.execute(duration_stmt)
        total_minutes = result.scalar() or 0.0
        
        total_hours = total_minutes / 60
        total_amount = total_hours * student.hourly_rate
        
        student_billing = StudentBillingItem(
            student_id=student.id,
            student_name=student.full_name,
            student_email=student.email,
            total_minutes=total_minutes,
            hourly_rate=student.hourly_rate,
            total_amount=round(total_amount, 2)
        )
        
        billing_month = f"{year}-{month:02d}"
        
        return FamilyBilling(
            family_id=student.id,
            family_number=f"STU-{student.id:04d}",
            parent_name=student.full_name,
            parent_email=student.email,
            students=[student_billing],
            total_family_amount=round(total_amount, 2),
            billing_month=billing_month
        )
    
    @staticmethod
    async def calculate_teacher_payroll(
        db: AsyncSession,
        teacher_id: int,
        year: int,
        month: int
    ) -> TeacherPayroll:
        """
        Calculate payroll for a specific teacher for a given month.
        Uses AuthUser model instead of deprecated Teacher model.
        """
        # Get teacher details from AuthUser
        teacher_stmt = select(AuthUser).where(
            AuthUser.id == teacher_id,
            AuthUser.role == AuthUserRole.TUTOR
        )
        teacher_result = await db.execute(teacher_stmt)
        teacher = teacher_result.scalars().first()
        
        if not teacher:
            raise ValueError(f"Teacher with id {teacher_id} not found")
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Calculate total duration for this teacher
        duration_stmt = select(func.sum(AttendanceLog.duration_minutes)).where(
            and_(
                AttendanceLog.teacher_id == teacher_id,
                AttendanceLog.join_time >= start_date,
                AttendanceLog.join_time < end_date
            )
        )
        
        result = await db.execute(duration_stmt)
        total_minutes = result.scalar() or 0.0
        
        # Get per-student breakdown using AuthUser for student info
        student_logs_stmt = select(
            AttendanceLog.student_id, 
            AuthUser.full_name.label('student_name'), 
            AuthUser.email.label('student_email'), 
            func.sum(AttendanceLog.duration_minutes).label('total_minutes')
        ).join(
            AuthUser, AttendanceLog.student_id == AuthUser.id
        ).where(
            and_(
                AttendanceLog.teacher_id == teacher_id,
                AttendanceLog.join_time >= start_date,
                AttendanceLog.join_time < end_date,
                AttendanceLog.student_id.isnot(None)
            )
        ).group_by(AttendanceLog.student_id, AuthUser.full_name, AuthUser.email)
        
        student_result = await db.execute(student_logs_stmt)
        student_rows = student_result.all()
        
        student_payroll_items = []
        for student_id, student_name, student_email, minutes in student_rows:
            student_payroll_items.append(StudentPayrollItem(
                student_id=student_id,
                student_name=student_name,
                student_email=student_email,
                total_minutes=float(minutes or 0)
            ))
        
        # Calculate payroll amount (convert minutes to hours)
        total_hours = total_minutes / 60
        total_amount = total_hours * teacher.hourly_rate
        
        billing_month = f"{year}-{month:02d}"
        
        return TeacherPayroll(
            teacher_id=teacher.id,
            teacher_name=teacher.full_name,
            teacher_email=teacher.email,
            total_minutes=total_minutes,
            hourly_rate=teacher.hourly_rate,
            total_amount=round(total_amount, 2),
            billing_month=billing_month,
            students=student_payroll_items
        )
    
    @staticmethod
    async def calculate_all_teachers_payroll(
        db: AsyncSession,
        year: int,
        month: int
    ) -> List[TeacherPayroll]:
        """
        Calculate payroll for all teachers for a given month.
        Uses AuthUser model with role TUTOR.
        """
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Get all tutors from AuthUser
        teachers_stmt = select(AuthUser).where(
            AuthUser.role == AuthUserRole.TUTOR,
            AuthUser.is_active == True
        )
        teachers_result = await db.execute(teachers_stmt)
        teachers = teachers_result.scalars().all()
        
        all_payrolls = []
        
        for teacher in teachers:
            try:
                # Calculate total duration for this teacher
                duration_stmt = select(func.sum(AttendanceLog.duration_minutes)).where(
                    and_(
                        AttendanceLog.teacher_id == teacher.id,
                        AttendanceLog.join_time >= start_date,
                        AttendanceLog.join_time < end_date
                    )
                )
                
                result = await db.execute(duration_stmt)
                total_minutes = result.scalar() or 0.0
                
                if total_minutes > 0:
                    # Get per-student breakdown
                    student_logs_stmt = select(
                        AttendanceLog.student_id, 
                        AuthUser.full_name.label('student_name'), 
                        AuthUser.email.label('student_email'), 
                        func.sum(AttendanceLog.duration_minutes).label('total_minutes')
                    ).join(
                        AuthUser, AttendanceLog.student_id == AuthUser.id
                    ).where(
                        and_(
                            AttendanceLog.teacher_id == teacher.id,
                            AttendanceLog.join_time >= start_date,
                            AttendanceLog.join_time < end_date,
                            AttendanceLog.student_id.isnot(None)
                        )
                    ).group_by(AttendanceLog.student_id, AuthUser.full_name, AuthUser.email)
                    
                    student_result = await db.execute(student_logs_stmt)
                    student_rows = student_result.all()
                    
                    student_payroll_items = []
                    for student_id, student_name, student_email, minutes in student_rows:
                        student_payroll_items.append(StudentPayrollItem(
                            student_id=student_id,
                            student_name=student_name,
                            student_email=student_email,
                            total_minutes=float(minutes or 0)
                        ))
                    
                    # Calculate payroll amount
                    total_hours = total_minutes / 60
                    total_amount = total_hours * teacher.hourly_rate
                    
                    billing_month = f"{year}-{month:02d}"
                    
                    payroll = TeacherPayroll(
                        teacher_id=teacher.id,
                        teacher_name=teacher.full_name,
                        teacher_email=teacher.email,
                        total_minutes=total_minutes,
                        hourly_rate=teacher.hourly_rate,
                        total_amount=round(total_amount, 2),
                        billing_month=billing_month,
                        students=student_payroll_items
                    )
                    
                    all_payrolls.append(payroll)
            except Exception as e:
                print(f"Error calculating payroll for teacher {teacher.id}: {e}")
                continue
        
        return all_payrolls
