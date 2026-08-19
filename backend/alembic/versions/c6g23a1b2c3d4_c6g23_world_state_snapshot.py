"""c6g23_world_state_snapshot

Revision ID: c6g23a1b2c3d4
Revises: c6g22a1b2c3d4
Create Date: 2026-08-02 02:40:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'c6g23a1b2c3d4'
down_revision: Union[str, None] = 'c6g22a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('world_state_snapshots',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('snapshot_id', sa.String(length=64), nullable=False),
        sa.Column('world_id', sa.UUID(), nullable=False),
        sa.Column('world_code', sa.String(length=64), nullable=False),
        sa.Column('world_version', sa.String(length=32), nullable=False),
        sa.Column('config_hash', sa.String(length=64), nullable=False),
        sa.Column('state_scope', sa.String(length=24), nullable=False),
        sa.Column('projection_as_of', sa.String(length=64), nullable=False),
        sa.Column('projection_manifest_hash', sa.String(length=64), nullable=False),
        sa.Column('aggregation_rule_version', sa.String(length=32), nullable=False),
        sa.Column('aggregation_config_hash', sa.String(length=64), nullable=False),
        sa.Column('source_manifest_hash', sa.String(length=64), nullable=False),
        sa.Column('dimensions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('truth_distribution', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('gaps', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('unknown', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('excluded', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('snapshot_hash', sa.String(length=64), nullable=False),
        sa.Column('is_stale', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['world_id'], ['vertical_worlds.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_world_state_snapshots_snapshot_id', 'world_state_snapshots', ['snapshot_id'], unique=True)
    op.create_index('ix_world_state_snapshots_snapshot_hash', 'world_state_snapshots', ['snapshot_hash'], unique=True)
    op.create_index('ix_world_state_snapshots_world_id', 'world_state_snapshots', ['world_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_world_state_snapshots_world_id', table_name='world_state_snapshots')
    op.drop_index('ix_world_state_snapshots_snapshot_hash', table_name='world_state_snapshots')
    op.drop_index('ix_world_state_snapshots_snapshot_id', table_name='world_state_snapshots')
    op.drop_table('world_state_snapshots')
