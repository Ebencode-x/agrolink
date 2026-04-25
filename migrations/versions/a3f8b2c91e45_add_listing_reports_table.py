"""add listing_reports table
Revision ID: a3f8b2c91e45
Revises: 2141dc5571fd
Create Date: 2026-04-25 17:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'a3f8b2c91e45'
down_revision = '2141dc5571fd'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('listing_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reporter_id', sa.Integer(), nullable=False),
        sa.Column('listing_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(length=200), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['listing_id'], ['market_listings.id']),
        sa.ForeignKeyConstraint(['reporter_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('reporter_id', 'listing_id', name='unique_report')
    )

def downgrade():
    op.drop_table('listing_reports')
