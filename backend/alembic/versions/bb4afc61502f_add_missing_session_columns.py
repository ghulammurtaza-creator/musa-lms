"""add_missing_session_columns

Revision ID: bb4afc61502f
Revises: 8d3bf161d499
Create Date: 2026-01-24 18:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb4afc61502f'
down_revision = '8d3bf161d499'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing columns to sessions table
    op.add_column('sessions', sa.Column('is_scheduled', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('sessions', sa.Column('google_meet_code', sa.String(255), nullable=True))
    op.add_column('sessions', sa.Column('google_calendar_event_id', sa.String(255), nullable=True))


def downgrade() -> None:
    # Remove the added columns
    op.drop_column('sessions', 'google_calendar_event_id')
    op.drop_column('sessions', 'google_meet_code')
    op.drop_column('sessions', 'is_scheduled')
