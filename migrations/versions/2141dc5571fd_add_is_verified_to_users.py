"""add is_verified to users
Revision ID: 2141dc5571fd
Revises:
Create Date: 2026-04-25 16:26:19.717363
"""
from alembic import op
import sqlalchemy as sa

revision = '2141dc5571fd'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_verified', sa.Boolean(), nullable=True))

def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('is_verified')
