"""add phone masking: conversations and messages

Revision ID: f3a9b2c1d5e7
Revises: 2141dc5571fd
Create Date: 2026-06-14

"""
from alembic import op
import sqlalchemy as sa

revision = 'f3a9b2c1d5e7'
down_revision = '0f9c4eaa82a1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'conversations',
        sa.Column('id',         sa.Integer(),     nullable=False),
        sa.Column('listing_id', sa.Integer(),     nullable=False),
        sa.Column('buyer_id',   sa.Integer(),     nullable=False),
        sa.Column('seller_id',  sa.Integer(),     nullable=False),
        sa.Column('status',     sa.Enum('active','closed','blocked',
                                        name='convstatus'), nullable=False,
                  server_default='active'),
        sa.Column('created_at', sa.DateTime(),    nullable=True),
        sa.Column('updated_at', sa.DateTime(),    nullable=True),
        sa.ForeignKeyConstraint(['listing_id'], ['market_listings.id']),
        sa.ForeignKeyConstraint(['buyer_id'],   ['users.id']),
        sa.ForeignKeyConstraint(['seller_id'],  ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('listing_id', 'buyer_id', name='uq_listing_buyer'),
    )
    op.create_index('ix_conv_buyer',  'conversations', ['buyer_id'])
    op.create_index('ix_conv_seller', 'conversations', ['seller_id'])

    op.create_table(
        'messages',
        sa.Column('id',              sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('sender_id',       sa.Integer(), nullable=False),
        sa.Column('body',            sa.Text(),    nullable=False),
        sa.Column('is_read',         sa.Boolean(), nullable=True,
                  server_default=sa.text('false')),
        sa.Column('sent_at',         sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id']),
        sa.ForeignKeyConstraint(['sender_id'],       ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_msg_conv', 'messages', ['conversation_id'])


def downgrade():
    op.drop_index('ix_msg_conv',     'messages')
    op.drop_table('messages')
    op.drop_index('ix_conv_seller',  'conversations')
    op.drop_index('ix_conv_buyer',   'conversations')
    op.drop_table('conversations')
    sa.Enum(name='convstatus').drop(op.get_bind())
