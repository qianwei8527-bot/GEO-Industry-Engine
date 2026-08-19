"""c6g16_demand_event

Revision ID: c6g16a1b2c3d4
Revises: c6g15a1b2c3d4
Create Date: 2026-08-02 00:10:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'c6g16a1b2c3d4'
down_revision: Union[str, None] = 'c6g15a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('demand_events',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('actor_id', sa.UUID(), nullable=True),
        sa.Column('actor_type', sa.String(length=32), nullable=False),
        sa.Column('actor_label', sa.String(length=255), nullable=True),
        sa.Column('scenario', sa.String(length=255), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('objective', sa.Text(), nullable=True),
        sa.Column('pain', sa.Text(), nullable=True),
        sa.Column('existing_solution', sa.Text(), nullable=True),
        sa.Column('missing_capability', sa.String(length=255), nullable=False),
        sa.Column('decision_stage', sa.String(length=32), nullable=False, server_default='research'),
        sa.Column('involved_nodes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('mentioned_nodes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ai_answer_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('matched_node_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('final_behavior', sa.String(length=32), nullable=False, server_default='none'),
        sa.Column('outcome', sa.String(length=32), nullable=False, server_default='pending'),
        sa.Column('impact_level', sa.String(length=16), nullable=False, server_default='medium'),
        sa.Column('priority', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('source', sa.String(length=32), nullable=False, server_default='user_report'),
        sa.Column('truth_status', sa.String(length=24), nullable=False, server_default='observed'),
        sa.Column('is_synthetic', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('may_affect_real_metrics', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('captured_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_demand_events_event_id', 'demand_events', ['event_id'], unique=True)
    op.create_index('ix_demand_events_actor_type', 'demand_events', ['actor_type'], unique=False)
    op.create_index('ix_demand_events_truth_status', 'demand_events', ['truth_status'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_demand_events_truth_status', table_name='demand_events')
    op.drop_index('ix_demand_events_actor_type', table_name='demand_events')
    op.drop_index('ix_demand_events_event_id', table_name='demand_events')
    op.drop_table('demand_events')
