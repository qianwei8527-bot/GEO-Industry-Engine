"""c6g03_candidate_change_node_fields

Revision ID: c6g03a1b2c3d4
Revises: c6g02a1b2c3d4
Create Date: 2026-08-01 17:30:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'c6g03a1b2c3d4'
down_revision: Union[str, None] = 'c6g02a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('candidate_changes', sa.Column('node_id', sa.String(length=64), nullable=True))
    op.create_index('ix_candidate_changes_node_id', 'candidate_changes', ['node_id'], unique=False)
    op.add_column('candidate_changes', sa.Column('source_id', sa.String(length=128), nullable=True))
    op.add_column('candidate_changes', sa.Column('source_evidence_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('candidate_changes', sa.Column('before_value', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('candidate_changes', sa.Column('proposed_value', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('candidate_changes', sa.Column('confidence_level', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('candidate_changes', sa.Column('impact_level', sa.String(length=16), nullable=False, server_default='low'))
    op.add_column('candidate_changes', sa.Column('deduplication_hash', sa.String(length=128), nullable=True))
    op.create_index('ix_candidate_changes_deduplication_hash', 'candidate_changes', ['deduplication_hash'], unique=False)
    op.add_column('candidate_changes', sa.Column('affected_engines', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('candidate_changes', sa.Column('applicable_rules', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('candidate_changes', sa.Column('review_status', sa.String(length=32), nullable=False, server_default='OBSERVED'))
    op.add_column('candidate_changes', sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('candidate_changes', sa.Column('applied_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('candidate_changes', sa.Column('actor_id', sa.String(length=128), nullable=True))
    op.add_column('candidate_changes', sa.Column('rejection_reason', sa.Text(), nullable=True))
    op.add_column('candidate_changes', sa.Column('applied_result', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column('candidate_changes', 'applied_result')
    op.drop_column('candidate_changes', 'rejection_reason')
    op.drop_column('candidate_changes', 'actor_id')
    op.drop_column('candidate_changes', 'applied_at')
    op.drop_column('candidate_changes', 'reviewed_at')
    op.drop_column('candidate_changes', 'review_status')
    op.drop_column('candidate_changes', 'applicable_rules')
    op.drop_column('candidate_changes', 'affected_engines')
    op.drop_index('ix_candidate_changes_deduplication_hash', table_name='candidate_changes')
    op.drop_column('candidate_changes', 'deduplication_hash')
    op.drop_column('candidate_changes', 'impact_level')
    op.drop_column('candidate_changes', 'confidence_level')
    op.drop_column('candidate_changes', 'proposed_value')
    op.drop_column('candidate_changes', 'before_value')
    op.drop_column('candidate_changes', 'source_evidence_ids')
    op.drop_column('candidate_changes', 'source_id')
    op.drop_index('ix_candidate_changes_node_id', table_name='candidate_changes')
    op.drop_column('candidate_changes', 'node_id')
