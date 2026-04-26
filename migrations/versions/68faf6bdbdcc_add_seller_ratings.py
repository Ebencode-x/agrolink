"""add seller ratings
Revision ID: 68faf6bdbdcc
Revises: a3f8b2c91e45
Create Date: 2026-04-26 15:11:18.760276
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = '68faf6bdbdcc'
down_revision = 'a3f8b2c91e45'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    if 'seller_ratings' not in inspector.get_table_names():
        op.create_table(
            'seller_ratings',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('seller_id', sa.Integer(), nullable=False),
            sa.Column('rater_id', sa.Integer(), nullable=False),
            sa.Column('listing_id', sa.Integer(), nullable=False),
            sa.Column('stars', sa.Integer(), nullable=False),
            sa.Column('comment', sa.String(length=300), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['listing_id'], ['market_listings.id']),
            sa.ForeignKeyConstraint(['rater_id'], ['users.id']),
            sa.ForeignKeyConstraint(['seller_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('rater_id', 'listing_id', name='unique_rating')
        )

def downgrade():
    op.drop_table('seller_ratings')
