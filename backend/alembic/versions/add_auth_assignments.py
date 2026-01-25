"""Add authentication and assignments tables

Revision ID: add_auth_assignments
Revises: 2ccce4224876
Create Date: 2026-01-23 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_auth_assignments'
down_revision = '2ccce4224876'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create auth_users table
    op.create_table(
        'auth_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('admin', 'tutor', 'student', name='authuserrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_auth_users_email'), 'auth_users', ['email'], unique=True)
    op.create_index(op.f('ix_auth_users_id'), 'auth_users', ['id'], unique=False)

    # Create student_tutor association table
    op.create_table(
        'student_tutor',
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('tutor_id', sa.Integer(), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['auth_users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tutor_id'], ['auth_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('student_id', 'tutor_id')
    )

    # Create assignments table
    op.create_table(
        'assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tutor_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('total_points', sa.Integer(), nullable=True, default=100),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tutor_id'], ['auth_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assignments_id'), 'assignments', ['id'], unique=False)

    # Create assignment_submissions table
    op.create_table(
        'assignment_submissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('assignment_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('submission_text', sa.Text(), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('status', sa.Enum('pending', 'submitted', 'graded', name='assignmentstatus'), nullable=True, default='pending'),
        sa.Column('grade', sa.Integer(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('graded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['assignment_id'], ['assignments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['auth_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assignment_submissions_id'), 'assignment_submissions', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_assignment_submissions_id'), table_name='assignment_submissions')
    op.drop_table('assignment_submissions')
    
    op.drop_index(op.f('ix_assignments_id'), table_name='assignments')
    op.drop_table('assignments')
    
    op.drop_table('student_tutor')
    
    op.drop_index(op.f('ix_auth_users_id'), table_name='auth_users')
    op.drop_index(op.f('ix_auth_users_email'), table_name='auth_users')
    op.drop_table('auth_users')
    
    # Drop enums
    sa.Enum(name='assignmentstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='authuserrole').drop(op.get_bind(), checkfirst=True)
