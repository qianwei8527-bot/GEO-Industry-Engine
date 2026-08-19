"""c6g24_world_state_transition

Revision ID: c6g24a1b2c3d4
Revises: c6g23a1b2c3d4
Create Date: 2026-08-02 03:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'c6g24a1b2c3d4'
down_revision: Union[str, None] = 'c6g23a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('world_state_transitions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('transition_id', sa.String(length=64), nullable=False),
        sa.Column('from_snapshot_id', sa.UUID(), nullable=False),
        sa.Column('to_snapshot_id', sa.UUID(), nullable=False),
        sa.Column('world_code', sa.String(length=64), nullable=False),
        sa.Column('world_version', sa.String(length=32), nullable=False),
        sa.Column('state_scope', sa.String(length=24), nullable=False),
        sa.Column('compatibility_result', sa.String(length=24), nullable=False),
        sa.Column('non_comparable_reason', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('from_snapshot_hash', sa.String(length=64), nullable=False),
        sa.Column('to_snapshot_hash', sa.String(length=64), nullable=False),
        sa.Column('transition_rule_version', sa.String(length=32), nullable=False),
        sa.Column('transition_config_hash', sa.String(length=64), nullable=False),
        sa.Column('change_manifest', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('gap_lifecycle', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('truth_scope_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('transition_hash', sa.String(length=64), nullable=False),
        sa.Column('historical_source_drift', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fully_auditable', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['from_snapshot_id'], ['world_state_snapshots.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['to_snapshot_id'], ['world_state_snapshots.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('from_snapshot_id', 'to_snapshot_id', 'transition_rule_version', 'transition_config_hash', name='uq_world_transition'),
    )
    op.create_index('ix_world_state_transitions_transition_id', 'world_state_transitions', ['transition_id'], unique=True)
    op.create_index('ix_world_state_transitions_transition_hash', 'world_state_transitions', ['transition_hash'], unique=True)
    op.create_index('ix_world_state_transitions_from_snapshot_id', 'world_state_transitions', ['from_snapshot_id'], unique=False)
    op.create_index('ix_world_state_transitions_to_snapshot_id', 'world_state_transitions', ['to_snapshot_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_world_state_transitions_to_snapshot_id', table_name='world_state_transitions')
    op.drop_index('ix_world_state_transitions_from_snapshot_id', table_name='world_state_transitions')
    op.drop_index('ix_world_state_transitions_transition_hash', table_name='world_state_transitions')
    op.drop_index('ix_world_state_transitions_transition_id', table_name='world_state_transitions')
    op.drop_table('world_state_transitions')
