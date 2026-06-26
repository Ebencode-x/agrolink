"""add phone_otps table
Revision ID: 438d8d2086a5
Revises: 488d804b058e
Create Date: 2026-06-26 14:09:25.056460
"""
from alembic import op
import sqlalchemy as sa

revision = '438d8d2086a5'
down_revision = '488d804b058e'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('phone_otps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('otp_code', sa.String(length=6), nullable=False),
        sa.Column('form_data', sa.Text(), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('verified', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('phone_otps', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_phone_otps_phone'), ['phone'], unique=False)

def downgrade():
    with op.batch_alter_table('phone_otps', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_phone_otps_phone'))
    op.drop_table('phone_otps')
