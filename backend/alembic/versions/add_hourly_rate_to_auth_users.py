"""Add hourly_rate to auth_users table

Revision ID: add_hourly_rate_auth_users
Revises: d523c6dada02
Create Date: 2026-02-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_hourly_rate_auth_users'
down_revision = 'd523c6dada02'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add hourly_rate column to auth_users table with default value
    op.add_column('auth_users', sa.Column('hourly_rate', sa.Float(), nullable=False, server_default='50.0'))
    
    # Remove the server_default after adding the column
    op.alter_column('auth_users', 'hourly_rate', server_default=None)


def downgrade() -> None:
    op.drop_column('auth_users', 'hourly_rate')
