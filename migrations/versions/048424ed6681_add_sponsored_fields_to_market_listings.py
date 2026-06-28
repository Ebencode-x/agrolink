"""add sponsored fields to market_listings

Revision ID: 048424ed6681
Revises: 6e6eb78698ba
Create Date: 2026-06-28 11:10:23.577758

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '048424ed6681'
down_revision = '6e6eb78698ba'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('market_listings', sa.Column('is_sponsored', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('market_listings', sa.Column('sponsored_until', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('market_listings', 'sponsored_until')
    op.drop_column('market_listings', 'is_sponsored')
