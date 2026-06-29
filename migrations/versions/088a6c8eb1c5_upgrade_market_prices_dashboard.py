"""upgrade_market_prices_dashboard
Revision ID: 088a6c8eb1c5
Revises: 23150e0a4a97
Create Date: 2026-06-29 09:48:50.640293
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '088a6c8eb1c5'
down_revision = '23150e0a4a97'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('market_prices', schema=None) as batch_op:
        # DROP columns za zamani
        batch_op.drop_column('avg_price')
        batch_op.drop_column('month')
        batch_op.drop_column('created_at')
        batch_op.drop_column('crop_name')
        # ADD columns mpya
        batch_op.add_column(sa.Column('crop_name', sa.String(length=100), nullable=False, server_default='Zao'))
        batch_op.add_column(sa.Column('price_tzs', sa.Numeric(12, 2), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('unit', sa.String(length=30), nullable=False, server_default='kg'))
        batch_op.add_column(sa.Column('source', sa.String(length=50), nullable=False, server_default='manual'))
        batch_op.add_column(sa.Column('recorded_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')))
        batch_op.add_column(sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True))
        batch_op.add_column(sa.Column('market', sa.String(length=120), nullable=True))
        # ALTER region
        batch_op.alter_column('region',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.String(length=100),
               existing_nullable=False,
               nullable=False,
               server_default='Kitaifa')

def downgrade():
    with op.batch_alter_table('market_prices', schema=None) as batch_op:
        batch_op.drop_column('created_by_id')
        batch_op.drop_column('crop_name')
        batch_op.drop_column('price_tzs')
        batch_op.drop_column('unit')
        batch_op.drop_column('source')
        batch_op.drop_column('recorded_at')
        batch_op.drop_column('market')
        batch_op.alter_column('region',
               existing_type=sa.String(length=100),
               type_=sa.VARCHAR(length=50),
               existing_nullable=False)
        batch_op.add_column(sa.Column('crop_name', sa.VARCHAR(length=50), nullable=False, server_default='Zao'))
        batch_op.add_column(sa.Column('avg_price', sa.DOUBLE_PRECISION(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('month', sa.VARCHAR(length=20), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
