"""update_attendance_logs_fkeys_to_auth_users

Revision ID: d523c6dada02
Revises: 1ebbb37ef30c
Create Date: 2026-01-24 17:48:09.652224

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd523c6dada02'
down_revision = '1ebbb37ef30c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop existing foreign key constraints
    op.drop_constraint('attendance_logs_teacher_id_fkey', 'attendance_logs', type_='foreignkey')
    op.drop_constraint('attendance_logs_student_id_fkey', 'attendance_logs', type_='foreignkey')
    
    # Add new foreign key constraints pointing to auth_users
    op.create_foreign_key(
        'attendance_logs_teacher_id_fkey',
        'attendance_logs', 'auth_users',
        ['teacher_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'attendance_logs_student_id_fkey',
        'attendance_logs', 'auth_users',
        ['student_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Revert back to old foreign keys
    op.drop_constraint('attendance_logs_teacher_id_fkey', 'attendance_logs', type_='foreignkey')
    op.drop_constraint('attendance_logs_student_id_fkey', 'attendance_logs', type_='foreignkey')
    
    op.create_foreign_key(
        'attendance_logs_teacher_id_fkey',
        'attendance_logs', 'teachers',
        ['teacher_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'attendance_logs_student_id_fkey',
        'attendance_logs', 'students',
        ['student_id'], ['id'],
        ondelete='CASCADE'
    )
