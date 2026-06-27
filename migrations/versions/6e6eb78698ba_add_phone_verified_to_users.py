"""add phone_verified to users

Revision ID: 6e6eb78698ba
Revises: 438d8d2086a5
Create Date: 2026-06-27 11:46:26.088995

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6e6eb78698ba'
down_revision = '438d8d2086a5'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('phone_verified', sa.Boolean(), nullable=False, server_default=sa.false()))

def downgrade():
    op.drop_column('users', 'phone_verified')
