"""add google_credentials to teachers

Revision ID: add_google_credentials
Revises: db5da8a25518
Create Date: 2026-01-16

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_google_credentials'
down_revision = 'db5da8a25518'
branch_labels = None
depends_on = None


def upgrade():
    # Add google_credentials column to teachers table
    op.add_column('teachers', sa.Column('google_credentials', sa.Text(), nullable=True))


def downgrade():
    # Remove google_credentials column from teachers table
    op.drop_column('teachers', 'google_credentials')
