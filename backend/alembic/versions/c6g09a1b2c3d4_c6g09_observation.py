"""c6g09_observation

Revision ID: c6g09a1b2c3d4
Revises: c6g08a1b2c3d4
Create Date: 2026-08-01 21:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'c6g09a1b2c3d4'
down_revision: Union[str, None] = 'c6g08a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('observation_sources',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('source_id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('source_type', sa.String(length=32), nullable=False),
    sa.Column('domain', sa.String(length=255), nullable=False),
    sa.Column('base_url', sa.String(length=1000), nullable=True),
    sa.Column('trust_tier', sa.String(length=16), nullable=False),
    sa.Column('node_id', sa.String(length=64), nullable=True),
    sa.Column('allowed_paths', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('denied_paths', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('parser_type', sa.String(length=32), nullable=False),
    sa.Column('schedule_minutes', sa.Integer(), nullable=False),
    sa.Column('rate_limit_seconds', sa.Integer(), nullable=False),
    sa.Column('timeout_seconds', sa.Integer(), nullable=False),
    sa.Column('max_content_size', sa.Integer(), nullable=False),
    sa.Column('allowed_content_types', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('enabled', sa.Boolean(), nullable=False),
    sa.Column('requires_review', sa.Boolean(), nullable=False),
    sa.Column('consecutive_failures', sa.Integer(), nullable=False),
    sa.Column('paused', sa.Boolean(), nullable=False),
    sa.Column('last_success_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('next_run_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('retention_days', sa.Integer(), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_observation_sources_source_id', 'observation_sources', ['source_id'], unique=True)
    op.create_index('ix_observation_sources_node_id', 'observation_sources', ['node_id'], unique=False)

    op.create_table('observation_runs',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('source_id', sa.String(length=64), nullable=False),
    sa.Column('node_id', sa.String(length=64), nullable=True),
    sa.Column('status', sa.String(length=24), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('http_status', sa.Integer(), nullable=True),
    sa.Column('content_hash', sa.String(length=64), nullable=True),
    sa.Column('previous_content_hash', sa.String(length=64), nullable=True),
    sa.Column('etag', sa.String(length=255), nullable=True),
    sa.Column('last_modified', sa.String(length=255), nullable=True),
    sa.Column('parser_version', sa.String(length=16), nullable=False),
    sa.Column('error_code', sa.String(length=32), nullable=True),
    sa.Column('retry_count', sa.Integer(), nullable=False),
    sa.Column('next_retry_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('candidates_found', sa.Integer(), nullable=False),
    sa.Column('change_created', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_observation_runs_source_id', 'observation_runs', ['source_id'], unique=False)
    op.create_index('ix_observation_runs_node_id', 'observation_runs', ['node_id'], unique=False)

    op.create_table('observation_artifacts',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('run_id', sa.UUID(), nullable=True),
    sa.Column('source_id', sa.String(length=64), nullable=False),
    sa.Column('node_id', sa.String(length=64), nullable=True),
    sa.Column('source_url', sa.String(length=1000), nullable=False),
    sa.Column('canonical_url', sa.String(length=1000), nullable=True),
    sa.Column('captured_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('content_hash', sa.String(length=64), nullable=False),
    sa.Column('content_type', sa.String(length=100), nullable=True),
    sa.Column('language', sa.String(length=16), nullable=True),
    sa.Column('title', sa.String(length=500), nullable=True),
    sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('extracted_text', sa.Text(), nullable=True),
    sa.Column('storage_reference', sa.String(length=500), nullable=True),
    sa.Column('source_trust_tier', sa.String(length=16), nullable=False),
    sa.Column('retention_until', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_observation_artifacts_source_id', 'observation_artifacts', ['source_id'], unique=False)
    op.create_index('ix_observation_artifacts_node_id', 'observation_artifacts', ['node_id'], unique=False)
    op.create_index('ix_observation_artifacts_content_hash', 'observation_artifacts', ['content_hash'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_observation_artifacts_content_hash', table_name='observation_artifacts')
    op.drop_index('ix_observation_artifacts_node_id', table_name='observation_artifacts')
    op.drop_index('ix_observation_artifacts_source_id', table_name='observation_artifacts')
    op.drop_table('observation_artifacts')
    op.drop_index('ix_observation_runs_node_id', table_name='observation_runs')
    op.drop_index('ix_observation_runs_source_id', table_name='observation_runs')
    op.drop_table('observation_runs')
    op.drop_index('ix_observation_sources_node_id', table_name='observation_sources')
    op.drop_index('ix_observation_sources_source_id', table_name='observation_sources')
    op.drop_table('observation_sources')
