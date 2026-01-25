"""add_google_credentials_to_auth_users

Revision ID: 1ebbb37ef30c
Revises: 2ccce4224876
Create Date: 2026-01-25 08:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1ebbb37ef30c'
down_revision = '2ccce4224876'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add google_credentials column to auth_users table
    op.add_column('auth_users', sa.Column('google_credentials', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove google_credentials column from auth_users table
    op.drop_column('auth_users', 'google_credentials')
