"""c6t1_transaction_persistence

Revision ID: c6t1a2b3c4d5e
Revises: c6a1b2c3d4e5
Create Date: 2026-08-01 16:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'c6t1a2b3c4d5e'
down_revision: Union[str, None] = 'c6a1b2c3d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('universe_transactions',
    sa.Column('transaction_id', sa.String(length=64), nullable=False),
    sa.Column('node_a_id', sa.String(length=64), nullable=False),
    sa.Column('node_b_id', sa.String(length=64), nullable=False),
    sa.Column('node_a_name', sa.String(length=255), nullable=True),
    sa.Column('node_b_name', sa.String(length=255), nullable=True),
    sa.Column('stage', sa.String(length=32), nullable=False),
    sa.Column('previous_stage', sa.String(length=32), nullable=False),
    sa.Column('scope_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('linked_opportunity_id', sa.String(length=64), nullable=True),
    sa.Column('relationship_id', sa.String(length=64), nullable=True),
    sa.Column('expected_value_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('milestone_count', sa.Integer(), nullable=False),
    sa.Column('milestones_completed', sa.Integer(), nullable=False),
    sa.Column('outcome_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('transaction_id')
    )
    op.create_index(op.f('ix_universe_transactions_node_a_id'), 'universe_transactions', ['node_a_id'], unique=False)
    op.create_index(op.f('ix_universe_transactions_node_b_id'), 'universe_transactions', ['node_b_id'], unique=False)

    op.create_table('transaction_events',
    sa.Column('event_id', sa.String(length=64), primary_key=True),
    sa.Column('transaction_id', sa.String(length=64), nullable=False),
    sa.Column('event_type', sa.String(length=32), nullable=False),
    sa.Column('actor_id', sa.String(length=64), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('milestone_index', sa.Integer(), nullable=False),
    sa.Column('details_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('event_id')
    )
    op.create_index(op.f('ix_transaction_events_transaction_id'), 'transaction_events', ['transaction_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_transaction_events_transaction_id'), table_name='transaction_events')
    op.drop_table('transaction_events')
    op.drop_index(op.f('ix_universe_transactions_node_b_id'), table_name='universe_transactions')
    op.drop_index(op.f('ix_universe_transactions_node_a_id'), table_name='universe_transactions')
    op.drop_table('universe_transactions')
