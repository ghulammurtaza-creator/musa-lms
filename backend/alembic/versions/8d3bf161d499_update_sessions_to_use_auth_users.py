"""update_sessions_to_use_auth_users

Revision ID: 8d3bf161d499
Revises: add_auth_assignments
Create Date: 2026-01-24 17:35:58.150392

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d3bf161d499'
down_revision = 'add_auth_assignments'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop existing foreign key constraint
    op.drop_constraint('sessions_teacher_id_fkey', 'sessions', type_='foreignkey')
    
    # Add new foreign key constraint pointing to auth_users
    op.create_foreign_key(
        'sessions_teacher_id_fkey',
        'sessions', 'auth_users',
        ['teacher_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Revert back to old foreign key
    op.drop_constraint('sessions_teacher_id_fkey', 'sessions', type_='foreignkey')
    
    op.create_foreign_key(
        'sessions_teacher_id_fkey',
        'sessions', 'teachers',
        ['teacher_id'], ['id'],
        ondelete='CASCADE'
    )
