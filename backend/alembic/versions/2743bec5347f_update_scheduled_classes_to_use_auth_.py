"""update_scheduled_classes_to_use_auth_users

Revision ID: 2743bec5347f
Revises: 571feedd1270
Create Date: 2026-01-24 17:27:36.319773

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2743bec5347f'
down_revision = '571feedd1270'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop existing foreign key constraints
    op.drop_constraint('scheduled_classes_teacher_id_fkey', 'scheduled_classes', type_='foreignkey')
    op.drop_constraint('scheduled_class_students_student_id_fkey', 'scheduled_class_students', type_='foreignkey')
    
    # Add new foreign key constraints pointing to auth_users
    op.create_foreign_key(
        'scheduled_classes_teacher_id_fkey',
        'scheduled_classes', 'auth_users',
        ['teacher_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'scheduled_class_students_student_id_fkey',
        'scheduled_class_students', 'auth_users',
        ['student_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Revert back to old foreign keys
    op.drop_constraint('scheduled_classes_teacher_id_fkey', 'scheduled_classes', type_='foreignkey')
    op.drop_constraint('scheduled_class_students_student_id_fkey', 'scheduled_class_students', type_='foreignkey')
    
    op.create_foreign_key(
        'scheduled_classes_teacher_id_fkey',
        'scheduled_classes', 'teachers',
        ['teacher_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'scheduled_class_students_student_id_fkey',
        'scheduled_class_students', 'students',
        ['student_id'], ['id'],
        ondelete='CASCADE'
    )
