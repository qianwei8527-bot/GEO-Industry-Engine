"""c6g17_demand_connection

Revision ID: c6g17a1b2c3d4
Revises: c6g16a1b2c3d4
Create Date: 2026-08-02 00:30:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'c6g17a1b2c3d4'
down_revision: Union[str, None] = 'c6g16a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('connection_candidates',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('candidate_id', sa.String(length=64), nullable=False),
        sa.Column('demand_event_id', sa.UUID(), nullable=False),
        sa.Column('source_node_id', sa.String(length=64), nullable=True),
        sa.Column('target_node_id', sa.String(length=64), nullable=False),
        sa.Column('connection_type', sa.String(length=32), nullable=False),
        sa.Column('matched_capabilities', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('evidence_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('capability_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('evidence_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('reputation_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('trust_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('connection_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('truth_status', sa.String(length=24), nullable=False, server_default='observed'),
        sa.Column('status', sa.String(length=24), nullable=False, server_default='proposed'),
        sa.Column('decision_source', sa.String(length=16), nullable=False, server_default='rule'),
        sa.Column('may_affect_real_metrics', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('outcome', sa.String(length=24), nullable=False, server_default='pending'),
        sa.Column('decided_by', sa.String(length=64), nullable=True),
        sa.Column('decision_reason', sa.Text(), nullable=True),
        sa.Column('rule_version', sa.String(length=32), nullable=False, server_default='1.0.0'),
        sa.Column('deduplication_hash', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['demand_event_id'], ['demand_events.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_connection_candidates_candidate_id', 'connection_candidates', ['candidate_id'], unique=True)
    op.create_index('ix_connection_candidates_demand_event_id', 'connection_candidates', ['demand_event_id'], unique=False)
    op.create_index('ix_connection_candidates_target_node_id', 'connection_candidates', ['target_node_id'], unique=False)
    op.create_index('ix_connection_candidates_deduplication_hash', 'connection_candidates', ['deduplication_hash'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_connection_candidates_deduplication_hash', table_name='connection_candidates')
    op.drop_index('ix_connection_candidates_target_node_id', table_name='connection_candidates')
    op.drop_index('ix_connection_candidates_demand_event_id', table_name='connection_candidates')
    op.drop_index('ix_connection_candidates_candidate_id', table_name='connection_candidates')
    op.drop_table('connection_candidates')
