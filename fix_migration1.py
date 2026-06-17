"""
Fix: Rewrite migration c07b850d1b86 to skip market_prices changes.
Trust columns + index cleanups tu — market_prices itashughulikiwa baadaye.
"""
import sys, os

MIGRATION_FILE = os.path.expanduser(
    "~/projects/agrolink/migrations/versions/c07b850d1b86_add_trust_system_columns.py"
)

CLEAN_MIGRATION = '''"""add trust system columns

Revision ID: c07b850d1b86
Revises: f3a9b2c1d5e7
Create Date: 2026-06-14 13:39:57.399703

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c07b850d1b86'
down_revision = 'f3a9b2c1d5e7'
branch_labels = None
depends_on = None


def upgrade():
    # ── Trust system columns on users ─────────────────────────────────────────
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('trust_level', sa.String(length=10),
                            server_default='gray', nullable=False))
        batch_op.add_column(sa.Column('trust_points', sa.Integer(),
                            server_default='0', nullable=False))
        batch_op.add_column(sa.Column('flag_count', sa.Integer(),
                            server_default='0', nullable=False))
        batch_op.add_column(sa.Column('transaction_count', sa.Integer(),
                            server_default='0', nullable=False))
        batch_op.add_column(sa.Column('avg_rating', sa.Float(),
                            server_default='0.0', nullable=False))
        batch_op.add_column(sa.Column('trust_updated_at', sa.DateTime(),
                            nullable=True))
        batch_op.add_column(sa.Column('can_post_listing', sa.Boolean(),
                            server_default='false', nullable=False))
        batch_op.add_column(sa.Column('can_advise', sa.Boolean(),
                            server_default='false', nullable=False))
        batch_op.add_column(sa.Column('can_b2b', sa.Boolean(),
                            server_default='false', nullable=False))

    # ── Index cleanups (hazina data — salama) ─────────────────────────────────
    with op.batch_alter_table('banned_emails', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_banned_emails_email'))
        batch_op.drop_index(batch_op.f('ix_banned_emails_phone'))
        batch_op.create_unique_constraint('uq_banned_email', ['email'])
        batch_op.create_unique_constraint('uq_banned_phone', ['phone'])

    with op.batch_alter_table('conversations', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_conv_buyer'))
        batch_op.drop_index(batch_op.f('ix_conv_seller'))

    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_msg_conv'))

    # NOTE: market_prices restructure imesimamishwa — itafanywa migration tofauti


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('can_b2b')
        batch_op.drop_column('can_advise')
        batch_op.drop_column('can_post_listing')
        batch_op.drop_column('trust_updated_at')
        batch_op.drop_column('avg_rating')
        batch_op.drop_column('transaction_count')
        batch_op.drop_column('flag_count')
        batch_op.drop_column('trust_points')
        batch_op.drop_column('trust_level')

    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.create_index('ix_msg_conv', ['conversation_id'], unique=False)

    with op.batch_alter_table('conversations', schema=None) as batch_op:
        batch_op.create_index('ix_conv_seller', ['seller_id'], unique=False)
        batch_op.create_index('ix_conv_buyer', ['buyer_id'], unique=False)

    with op.batch_alter_table('banned_emails', schema=None) as batch_op:
        batch_op.drop_constraint('uq_banned_email', type_='unique')
        batch_op.drop_constraint('uq_banned_phone', type_='unique')
        batch_op.create_index('ix_banned_emails_phone', ['phone'], unique=True)
        batch_op.create_index('ix_banned_emails_email', ['email'], unique=True)
'''

with open(MIGRATION_FILE, "w") as f:
    f.write(CLEAN_MIGRATION)

print("✅ Migration file rewritten — market_prices block removed")
print("   Trust columns sasa zina server_default — hazitakataa rows zilizopo")
print()
print("⏭  Sasa run: flask db upgrade")
