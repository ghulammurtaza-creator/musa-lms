from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime
from typing import List
from app.models.models import Family, Student, Teacher, AttendanceLog
from app.schemas.schemas import FamilyBilling, StudentBillingItem, TeacherPayroll, StudentPayrollItem
from app.services.duration_service import DurationCalculationEngine


class BillingService:
    """Service for handling family billing and teacher payroll calculations"""
    
    @staticmethod
    async def calculate_family_billing(
        db: AsyncSession,
        family_id: int,
        year: int,
        month: int
    ) -> FamilyBilling:
        """
        Calculate billing for a specific family for a given month.
        Aggregates all students in the family.
        """
        # Get family details
        family_stmt = select(Family).where(Family.id == family_id)
        family_result = await db.execute(family_stmt)
        family = family_result.scalars().first()
        
        if not family:
            raise ValueError(f"Family with id {family_id} not found")
        
        # Get all students in the family
        students_stmt = select(Student).where(Student.family_id == family_id)
        students_result = await db.execute(students_stmt)
        students = students_result.scalars().all()
        
        student_billing_items = []
        total_family_amount = 0.0
        
        for student in students:
            # Calculate total duration for this student
            total_minutes = await DurationCalculationEngine.calculate_student_monthly_duration(
                db, student.id, year, month
            )
            
            # Calculate billing amount (convert minutes to hours)
            total_hours = total_minutes / 60
            total_amount = total_hours * student.hourly_rate
            total_family_amount += total_amount
            
            student_billing_items.append(StudentBillingItem(
                student_id=student.id,
                student_name=student.name,
                student_email=student.email,
                total_minutes=total_minutes,
                hourly_rate=student.hourly_rate,
                total_amount=round(total_amount, 2)
            ))
        
        billing_month = f"{year}-{month:02d}"
        
        return FamilyBilling(
            family_id=family.id,
            family_number=family.family_number,
            parent_name=family.parent_name,
            parent_email=family.parent_email,
            students=student_billing_items,
            total_family_amount=round(total_family_amount, 2),
            billing_month=billing_month
        )
    
    @staticmethod
    async def calculate_all_families_billing(
        db: AsyncSession,
        year: int,
        month: int
    ) -> List[FamilyBilling]:
        """
        Calculate billing for all families for a given month.
        """
        # Get all families
        families_stmt = select(Family)
        families_result = await db.execute(families_stmt)
        families = families_result.scalars().all()
        
        all_billings = []
        
        for family in families:
            try:
                billing = await BillingService.calculate_family_billing(
                    db, family.id, year, month
                )
                # Only include families with activity
                if billing.total_family_amount > 0:
                    all_billings.append(billing)
            except Exception as e:
                print(f"Error calculating billing for family {family.id}: {e}")
                continue
        
        return all_billings
    
    @staticmethod
    async def calculate_teacher_payroll(
        db: AsyncSession,
        teacher_id: int,
        year: int,
        month: int
    ) -> TeacherPayroll:
        """
        Calculate payroll for a specific teacher for a given month.
        Includes per-student breakdown.
        """
        # Get teacher details
        teacher_stmt = select(Teacher).where(Teacher.id == teacher_id)
        teacher_result = await db.execute(teacher_stmt)
        teacher = teacher_result.scalars().first()
        
        if not teacher:
            raise ValueError(f"Teacher with id {teacher_id} not found")
        
        # Calculate total duration for this teacher
        total_minutes = await DurationCalculationEngine.calculate_teacher_monthly_duration(
            db, teacher_id, year, month
        )
        
        # Get per-student breakdown
        # Find all students this teacher taught in the given month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Query attendance logs to get unique students
        student_logs_stmt = select(AttendanceLog.student_id, Student.name, Student.email, func.sum(AttendanceLog.duration_minutes).label('total_minutes')).join(
            Student, AttendanceLog.student_id == Student.id
        ).where(
            and_(
                AttendanceLog.teacher_id == teacher_id,
                AttendanceLog.join_time >= start_date,
                AttendanceLog.join_time < end_date,
                AttendanceLog.student_id.isnot(None)
            )
        ).group_by(AttendanceLog.student_id, Student.name, Student.email)
        
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
            teacher_name=teacher.name,
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
        """
        # Get all teachers
        teachers_stmt = select(Teacher)
        teachers_result = await db.execute(teachers_stmt)
        teachers = teachers_result.scalars().all()
        
        all_payrolls = []
        
        for teacher in teachers:
            try:
                payroll = await BillingService.calculate_teacher_payroll(
                    db, teacher.id, year, month
                )
                # Only include teachers with activity
                if payroll.total_amount > 0:
                    all_payrolls.append(payroll)
            except Exception as e:
                print(f"Error calculating payroll for teacher {teacher.id}: {e}")
                continue
        
        return all_payrolls
