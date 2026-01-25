"""add_display_name_to_attendance_logs

Revision ID: 2ccce4224876
Revises: bb4afc61502f
Create Date: 2026-01-16 16:08:59.065569

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ccce4224876'
down_revision = 'bb4afc61502f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add display_name column to attendance_logs table
    op.add_column('attendance_logs', sa.Column('display_name', sa.String(255), nullable=True))


def downgrade() -> None:
    # Remove display_name column from attendance_logs table
    op.drop_column('attendance_logs', 'display_name')
