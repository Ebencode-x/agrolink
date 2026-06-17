#!/usr/bin/env python3
"""
Fix migration 4fbd0f4eed9a:
- Ondoa market_prices changes (zinachanganya, hazihusiani na task hii)
- Ongeza is_deleted + reply_to_id kwenye messages tu
"""
from pathlib import Path
import sys

MIG = Path.home() / "projects/agrolink/migrations/versions/4fbd0f4eed9a_add_is_deleted_reply_to_id_to_messages.py"

if not MIG.exists():
    print(f"IMEKOSEKANA: {MIG}"); sys.exit(1)

NEW_CONTENT = '''"""add is_deleted reply_to_id to messages
Revision ID: 4fbd0f4eed9a
Revises: c07b850d1b86
Create Date: 2026-06-16 21:39:32.055608
"""
from alembic import op
import sqlalchemy as sa

revision = '4fbd0f4eed9a'
down_revision = 'c07b850d1b86'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'))
        batch_op.add_column(sa.Column('reply_to_id', sa.Integer(), sa.ForeignKey('messages.id'), nullable=True))

def downgrade():
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.drop_column('reply_to_id')
        batch_op.drop_column('is_deleted')
'''

MIG.write_text(NEW_CONTENT, encoding="utf-8")
print("✅ Migration imefixiwa — messages columns tu.")
print("\nSasa run:")
print("  source venv/bin/activate")
print("  flask db upgrade")
print("  deactivate")
