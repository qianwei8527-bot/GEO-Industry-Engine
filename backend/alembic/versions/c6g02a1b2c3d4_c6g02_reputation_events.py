"""c6g02_reputation_events

Revision ID: c6g02a1b2c3d4
Revises: c6t1a2b3c4d5e
Create Date: 2026-08-01 17:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'c6g02a1b2c3d4'
down_revision: Union[str, None] = 'c6t1a2b3c4d5e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('reputation_events',
    sa.Column('event_id', sa.String(length=64), nullable=False),
    sa.Column('node_id', sa.String(length=64), nullable=False),
    sa.Column('node_type', sa.String(length=32), nullable=False),
    sa.Column('event_type', sa.String(length=64), nullable=False),
    sa.Column('dimension', sa.String(length=32), nullable=False),
    sa.Column('impact', sa.String(length=16), nullable=False),
    sa.Column('base_weight', sa.Float(), nullable=False),
    sa.Column('evidence_weight', sa.Float(), nullable=False),
    sa.Column('source_type', sa.String(length=32), nullable=False),
    sa.Column('source_id', sa.String(length=128), nullable=True),
    sa.Column('source_weight', sa.Float(), nullable=False),
    sa.Column('effective_weight', sa.Float(), nullable=False),
    sa.Column('evidence_refs', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
    sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('event_id')
    )
    op.create_index(op.f('ix_reputation_events_node_id'), 'reputation_events', ['node_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_reputation_events_node_id'), table_name='reputation_events')
    op.drop_table('reputation_events')
