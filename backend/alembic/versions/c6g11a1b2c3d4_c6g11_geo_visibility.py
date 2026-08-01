"""c6g11_geo_visibility

Revision ID: c6g11a1b2c3d4
Revises: c6g10a1b2c3d4
Create Date: 2026-08-01 23:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'c6g11a1b2c3d4'
down_revision: Union[str, None] = 'c6g10a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('question_sets',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('set_key', sa.String(length=64), nullable=False),
    sa.Column('industry_id', sa.String(length=64), nullable=True),
    sa.Column('category', sa.String(length=64), nullable=False),
    sa.Column('user_intent', sa.String(length=255), nullable=True),
    sa.Column('audience', sa.String(length=255), nullable=True),
    sa.Column('region', sa.String(length=64), nullable=True),
    sa.Column('language', sa.String(length=16), nullable=False),
    sa.Column('question_text', sa.Text(), nullable=False),
    sa.Column('target_entities', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('competitor_entities', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('enabled', sa.Boolean(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_question_sets_set_key', 'question_sets', ['set_key'], unique=True)

    op.create_table('ai_observation_runs',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('provider', sa.String(length=32), nullable=False),
    sa.Column('model', sa.String(length=64), nullable=False),
    sa.Column('model_version', sa.String(length=64), nullable=True),
    sa.Column('question_set_version', sa.Integer(), nullable=False),
    sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('status', sa.String(length=24), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('latency_ms', sa.Integer(), nullable=True),
    sa.Column('token_usage', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('estimated_cost', sa.Float(), nullable=True),
    sa.Column('request_id', sa.String(length=128), nullable=True),
    sa.Column('retry_count', sa.Integer(), nullable=False),
    sa.Column('error', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('ai_answer_artifacts',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('run_id', sa.UUID(), nullable=True),
    sa.Column('question_id', sa.UUID(), nullable=True),
    sa.Column('provider', sa.String(length=32), nullable=False),
    sa.Column('model', sa.String(length=64), nullable=False),
    sa.Column('raw_answer', sa.Text(), nullable=False),
    sa.Column('normalized_answer', sa.Text(), nullable=True),
    sa.Column('answer_hash', sa.String(length=64), nullable=False),
    sa.Column('captured_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('citations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('entity_mentions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('recommendation_order', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('uncertainty', sa.String(length=32), nullable=True),
    sa.Column('parser_version', sa.String(length=16), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ai_answer_artifacts_run_id', 'ai_answer_artifacts', ['run_id'], unique=False)
    op.create_index('ix_ai_answer_artifacts_question_id', 'ai_answer_artifacts', ['question_id'], unique=False)

    op.create_table('visibility_results',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('node_id', sa.String(length=64), nullable=False),
    sa.Column('provider', sa.String(length=32), nullable=False),
    sa.Column('question_id', sa.UUID(), nullable=True),
    sa.Column('metric_key', sa.String(length=64), nullable=False),
    sa.Column('metric_value', sa.Float(), nullable=False),
    sa.Column('sample_size', sa.Integer(), nullable=False),
    sa.Column('provider_count', sa.Integer(), nullable=False),
    sa.Column('question_count', sa.Integer(), nullable=False),
    sa.Column('captured_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('confidence', sa.Float(), nullable=False),
    sa.Column('calculation_version', sa.String(length=16), nullable=False),
    sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_visibility_results_node_id', 'visibility_results', ['node_id'], unique=False)
    op.create_index('ix_visibility_results_metric_key', 'visibility_results', ['metric_key'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_visibility_results_metric_key', table_name='visibility_results')
    op.drop_index('ix_visibility_results_node_id', table_name='visibility_results')
    op.drop_table('visibility_results')
    op.drop_index('ix_ai_answer_artifacts_question_id', table_name='ai_answer_artifacts')
    op.drop_index('ix_ai_answer_artifacts_run_id', table_name='ai_answer_artifacts')
    op.drop_table('ai_answer_artifacts')
    op.drop_table('ai_observation_runs')
    op.drop_index('ix_question_sets_set_key', table_name='question_sets')
    op.drop_table('question_sets')
