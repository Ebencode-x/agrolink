"""add orders table
Revision ID: cd5758152e72
Revises: a354710ade85
Create Date: 2026-06-17
"""
from alembic import op
import sqlalchemy as sa

revision = 'cd5758152e72'
down_revision = 'a354710ade85'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('conversation_id', sa.Integer(), nullable=False),
    sa.Column('buyer_id', sa.Integer(), nullable=False),
    sa.Column('seller_id', sa.Integer(), nullable=False),
    sa.Column('listing_id', sa.Integer(), nullable=False),
    sa.Column('quantity_kg', sa.Float(), nullable=False),
    sa.Column('price_tzs', sa.BigInteger(), nullable=False),
    sa.Column('status', sa.Enum('draft','submitted','approved','paid','completed','cancelled', name='orderstatus'), nullable=False),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['buyer_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
    sa.ForeignKeyConstraint(['listing_id'], ['market_listings.id'], ),
    sa.ForeignKeyConstraint(['seller_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('conversation_id')
    )

def downgrade():
    op.drop_table('orders')
