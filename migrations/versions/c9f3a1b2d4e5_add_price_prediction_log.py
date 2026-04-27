"""add price prediction log

Revision ID: c9f3a1b2d4e5
Revises: 68faf6bdbdcc
Create Date: 2026-04-27 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = 'c9f3a1b2d4e5'
down_revision = '68faf6bdbdcc'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    if 'price_prediction_logs' not in inspector.get_table_names():
        op.create_table(
            'price_prediction_logs',
            sa.Column('id',          sa.Integer(),     nullable=False),
            sa.Column('crop_name',   sa.String(100),   nullable=False),
            sa.Column('region',      sa.String(80),    nullable=False),
            sa.Column('month',       sa.String(20),    nullable=False),
            sa.Column('season',      sa.String(30),    nullable=True),
            sa.Column('user_id',     sa.Integer(),     nullable=True),
            sa.Column('ai_response', sa.Text(),        nullable=True),
            sa.Column('queried_at',  sa.DateTime(),    nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
        )
        print("  Table price_prediction_logs created.")
    else:
        print("  Table price_prediction_logs already exists — skipped.")


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    if 'price_prediction_logs' in inspector.get_table_names():
        op.drop_table('price_prediction_logs')
