"""Initial migration - create all tables

Revision ID: 001
Revises: 
Create Date: 2026-01-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create families table
    op.create_table(
        'families',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('family_number', sa.String(length=50), nullable=False),
        sa.Column('parent_name', sa.String(length=255), nullable=False),
        sa.Column('parent_email', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_families_family_number'), 'families', ['family_number'], unique=True)
    op.create_index(op.f('ix_families_id'), 'families', ['id'], unique=False)

    # Create teachers table
    op.create_table(
        'teachers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hourly_rate', sa.Float(), nullable=False),
        sa.Column('subject_specialties', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_teachers_email'), 'teachers', ['email'], unique=True)
    op.create_index(op.f('ix_teachers_id'), 'teachers', ['id'], unique=False)

    # Create students table
    op.create_table(
        'students',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('family_id', sa.Integer(), nullable=False),
        sa.Column('hourly_rate', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['family_id'], ['families.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_students_email'), 'students', ['email'], unique=True)
    op.create_index(op.f('ix_students_id'), 'students', ['id'], unique=False)

    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('meeting_id', sa.String(length=255), nullable=False),
        sa.Column('teacher_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ai_summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sessions_meeting_id'), 'sessions', ['meeting_id'], unique=True)
    op.create_index(op.f('ix_sessions_id'), 'sessions', ['id'], unique=False)

    # Create attendance_logs table
    op.create_table(
        'attendance_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('user_email', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('Teacher', 'Student', name='userrole'), nullable=False),
        sa.Column('teacher_id', sa.Integer(), nullable=True),
        sa.Column('student_id', sa.Integer(), nullable=True),
        sa.Column('join_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('exit_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_minutes', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_attendance_logs_id'), 'attendance_logs', ['id'], unique=False)
    op.create_index(op.f('ix_attendance_logs_user_email'), 'attendance_logs', ['user_email'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_attendance_logs_user_email'), table_name='attendance_logs')
    op.drop_index(op.f('ix_attendance_logs_id'), table_name='attendance_logs')
    op.drop_table('attendance_logs')
    
    op.drop_index(op.f('ix_sessions_id'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_meeting_id'), table_name='sessions')
    op.drop_table('sessions')
    
    op.drop_index(op.f('ix_students_id'), table_name='students')
    op.drop_index(op.f('ix_students_email'), table_name='students')
    op.drop_table('students')
    
    op.drop_index(op.f('ix_teachers_id'), table_name='teachers')
    op.drop_index(op.f('ix_teachers_email'), table_name='teachers')
    op.drop_table('teachers')
    
    op.drop_index(op.f('ix_families_id'), table_name='families')
    op.drop_index(op.f('ix_families_family_number'), table_name='families')
    op.drop_table('families')
    
    # Drop enum type
    sa.Enum(name='userrole').drop(op.get_bind(), checkfirst=True)
