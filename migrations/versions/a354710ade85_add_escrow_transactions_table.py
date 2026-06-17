"""add escrow_transactions table
Revision ID: a354710ade85
Revises: 4fbd0f4eed9a
Create Date: 2026-06-17 18:06:42.671208
"""
from alembic import op
import sqlalchemy as sa

revision = 'a354710ade85'
down_revision = '4fbd0f4eed9a'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('escrow_transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('conversation_id', sa.Integer(), nullable=False),
    sa.Column('buyer_id', sa.Integer(), nullable=False),
    sa.Column('seller_id', sa.Integer(), nullable=False),
    sa.Column('amount_tzs', sa.BigInteger(), nullable=False),
    sa.Column('status', sa.Enum('held', 'released', 'refunded', name='escrowstatus'), nullable=False),
    sa.Column('reference', sa.String(length=32), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['buyer_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
    sa.ForeignKeyConstraint(['seller_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('reference')
    )

def downgrade():
    op.drop_table('escrow_transactions')
