"""v10p0_realm_project

Revision ID: v10p0a1b2c3d4
Revises: c6g24a1b2c3d4
Create Date: 2026-08-03 10:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'v10p0a1b2c3d4'
down_revision: Union[str, None] = 'c6g24a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('realm_registry',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('entity_id', sa.UUID(), nullable=False),
        sa.Column('entity_type', sa.String(length=32), nullable=False),
        sa.Column('realm_type', sa.String(length=32), nullable=False),
        sa.Column('realm_code', sa.String(length=64), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('lifecycle_state', sa.String(length=24), nullable=False),
        sa.Column('claim_status', sa.String(length=16), nullable=False),
        sa.Column('owner_id', sa.UUID(), nullable=True),
        sa.Column('source', sa.String(length=32), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['entity_id'], ['entities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('entity_id'),
        sa.UniqueConstraint('realm_code'),
    )
    op.create_index('ix_realm_registry_realm_code', 'realm_registry', ['realm_code'], unique=True)
    op.create_index('ix_realm_registry_owner_id', 'realm_registry', ['owner_id'], unique=False)
    op.create_index('ix_realm_registry_entity_id', 'realm_registry', ['entity_id'], unique=False)

    op.create_table('realm_claims',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('entity_id', sa.UUID(), nullable=False),
        sa.Column('claimant_id', sa.UUID(), nullable=False),
        sa.Column('claim_type', sa.String(length=24), nullable=False),
        sa.Column('status', sa.String(length=16), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('decided_by', sa.UUID(), nullable=True),
        sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['entity_id'], ['entities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_realm_claims_entity_id', 'realm_claims', ['entity_id'], unique=False)
    op.create_index('ix_realm_claims_claimant_id', 'realm_claims', ['claimant_id'], unique=False)

    op.create_table('realm_data_authorizations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('authorization_code', sa.String(length=64), nullable=False),
        sa.Column('entity_id', sa.UUID(), nullable=False),
        sa.Column('owner_id', sa.UUID(), nullable=False),
        sa.Column('granted_to_id', sa.UUID(), nullable=True),
        sa.Column('source_name', sa.String(length=255), nullable=True),
        sa.Column('source_url', sa.String(length=1000), nullable=True),
        sa.Column('source_type', sa.String(length=100), nullable=True),
        sa.Column('license', sa.String(length=255), nullable=True),
        sa.Column('use_scope', sa.String(length=64), nullable=False),
        sa.Column('valid_from', sa.DateTime(timezone=True), nullable=True),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('truth_status', sa.String(length=24), nullable=False),
        sa.Column('may_affect_real_metrics', sa.Boolean(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['entity_id'], ['entities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('authorization_code'),
    )
    op.create_index('ix_realm_data_authorizations_authorization_code', 'realm_data_authorizations', ['authorization_code'], unique=True)
    op.create_index('ix_realm_data_authorizations_entity_id', 'realm_data_authorizations', ['entity_id'], unique=False)
    op.create_index('ix_realm_data_authorizations_owner_id', 'realm_data_authorizations', ['owner_id'], unique=False)

    op.create_table('geo_projects',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('project_code', sa.String(length=64), nullable=False),
        sa.Column('realm_id', sa.UUID(), nullable=False),
        sa.Column('realm_entity_id', sa.UUID(), nullable=True),
        sa.Column('project_type', sa.String(length=24), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('objective', sa.Text(), nullable=True),
        sa.Column('target_brand', sa.String(length=255), nullable=True),
        sa.Column('target_product', sa.String(length=255), nullable=True),
        sa.Column('target_audience', sa.Text(), nullable=True),
        sa.Column('scenario', sa.Text(), nullable=True),
        sa.Column('problems', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ai_platforms', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('question_set', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('competitors', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('expected_outcome', sa.Text(), nullable=True),
        sa.Column('lifecycle_state', sa.String(length=24), nullable=False),
        sa.Column('status', sa.String(length=24), nullable=False),
        sa.Column('operator_id', sa.UUID(), nullable=True),
        sa.Column('source', sa.String(length=32), nullable=False),
        sa.Column('truth_status', sa.String(length=24), nullable=False),
        sa.Column('may_affect_real_metrics', sa.Boolean(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['realm_id'], ['realm_registry.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_code'),
    )
    op.create_index('ix_geo_projects_project_code', 'geo_projects', ['project_code'], unique=True)
    op.create_index('ix_geo_projects_realm_id', 'geo_projects', ['realm_id'], unique=False)
    op.create_index('ix_geo_projects_realm_entity_id', 'geo_projects', ['realm_entity_id'], unique=False)

    op.create_table('realm_data_assets',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('entity_id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=True),
        sa.Column('authorization_id', sa.UUID(), nullable=True),
        sa.Column('asset_type', sa.String(length=32), nullable=False),
        sa.Column('asset_key', sa.String(length=128), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.UUID(), nullable=False),
        sa.Column('source_ref', sa.String(length=1000), nullable=True),
        sa.Column('truth_status', sa.String(length=24), nullable=False),
        sa.Column('may_affect_real_metrics', sa.Boolean(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['authorization_id'], ['realm_data_authorizations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['entity_id'], ['entities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['geo_projects.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('entity_id', 'asset_key', name='uq_realm_data_asset_entity_key'),
    )
    op.create_index('ix_realm_data_assets_entity_id', 'realm_data_assets', ['entity_id'], unique=False)
    op.create_index('ix_realm_data_assets_project_id', 'realm_data_assets', ['project_id'], unique=False)
    op.create_index('ix_realm_data_assets_asset_key', 'realm_data_assets', ['asset_key'], unique=False)
    op.create_index('ix_realm_data_assets_owner_id', 'realm_data_assets', ['owner_id'], unique=False)

    op.create_table('project_work_items',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('work_type', sa.String(length=32), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=24), nullable=False),
        sa.Column('operator_id', sa.UUID(), nullable=True),
        sa.Column('input_manifest', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('output_manifest', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('source_fact_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('truth_status', sa.String(length=24), nullable=False),
        sa.Column('may_affect_real_metrics', sa.Boolean(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['geo_projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_project_work_items_project_id', 'project_work_items', ['project_id'], unique=False)

    op.create_table('project_artifacts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('work_item_id', sa.UUID(), nullable=True),
        sa.Column('artifact_type', sa.String(length=32), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('content_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('content_text', sa.Text(), nullable=True),
        sa.Column('citations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=24), nullable=False),
        sa.Column('operator_id', sa.UUID(), nullable=True),
        sa.Column('authorization_scope', sa.String(length=64), nullable=True),
        sa.Column('source_fact_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('truth_status', sa.String(length=24), nullable=False),
        sa.Column('may_affect_real_metrics', sa.Boolean(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['geo_projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['work_item_id'], ['project_work_items.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_project_artifacts_project_id', 'project_artifacts', ['project_id'], unique=False)
    op.create_index('ix_project_artifacts_work_item_id', 'project_artifacts', ['work_item_id'], unique=False)

    op.create_table('tool_execution_records',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('execution_code', sa.String(length=64), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=True),
        sa.Column('realm_id', sa.UUID(), nullable=True),
        sa.Column('work_item_id', sa.UUID(), nullable=True),
        sa.Column('operator_id', sa.UUID(), nullable=False),
        sa.Column('provider', sa.String(length=64), nullable=False),
        sa.Column('tool_name', sa.String(length=64), nullable=False),
        sa.Column('model_name', sa.String(length=128), nullable=True),
        sa.Column('model_version', sa.String(length=64), nullable=True),
        sa.Column('input_manifest', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('output_manifest', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('source_fact_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('truth_status', sa.String(length=24), nullable=False),
        sa.Column('cost', sa.Float(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('execution_status', sa.String(length=24), nullable=False),
        sa.Column('config_version', sa.String(length=32), nullable=False),
        sa.Column('config_hash', sa.String(length=64), nullable=True),
        sa.Column('citations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['geo_projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['work_item_id'], ['project_work_items.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('execution_code'),
    )
    op.create_index('ix_tool_execution_records_execution_code', 'tool_execution_records', ['execution_code'], unique=True)
    op.create_index('ix_tool_execution_records_project_id', 'tool_execution_records', ['project_id'], unique=False)
    op.create_index('ix_tool_execution_records_realm_id', 'tool_execution_records', ['realm_id'], unique=False)
    op.create_index('ix_tool_execution_records_work_item_id', 'tool_execution_records', ['work_item_id'], unique=False)
    op.create_index('ix_tool_execution_records_operator_id', 'tool_execution_records', ['operator_id'], unique=False)

    op.create_table('project_outcomes',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('outcome_code', sa.String(length=64), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('outcome_type', sa.String(length=32), nullable=False),
        sa.Column('claim_text', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=24), nullable=False),
        sa.Column('evidence_claim_id', sa.UUID(), nullable=True),
        sa.Column('truth_status', sa.String(length=24), nullable=False),
        sa.Column('operator_id', sa.UUID(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['evidence_claim_id'], ['evidence_claims.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['project_id'], ['geo_projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('outcome_code'),
    )
    op.create_index('ix_project_outcomes_outcome_code', 'project_outcomes', ['outcome_code'], unique=True)
    op.create_index('ix_project_outcomes_project_id', 'project_outcomes', ['project_id'], unique=False)
    op.create_index('ix_project_outcomes_evidence_claim_id', 'project_outcomes', ['evidence_claim_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_project_outcomes_evidence_claim_id', table_name='project_outcomes')
    op.drop_index('ix_project_outcomes_project_id', table_name='project_outcomes')
    op.drop_index('ix_project_outcomes_outcome_code', table_name='project_outcomes')
    op.drop_table('project_outcomes')
    op.drop_index('ix_tool_execution_records_operator_id', table_name='tool_execution_records')
    op.drop_index('ix_tool_execution_records_work_item_id', table_name='tool_execution_records')
    op.drop_index('ix_tool_execution_records_realm_id', table_name='tool_execution_records')
    op.drop_index('ix_tool_execution_records_project_id', table_name='tool_execution_records')
    op.drop_index('ix_tool_execution_records_execution_code', table_name='tool_execution_records')
    op.drop_table('tool_execution_records')
    op.drop_index('ix_project_artifacts_work_item_id', table_name='project_artifacts')
    op.drop_index('ix_project_artifacts_project_id', table_name='project_artifacts')
    op.drop_table('project_artifacts')
    op.drop_index('ix_project_work_items_project_id', table_name='project_work_items')
    op.drop_table('project_work_items')
    op.drop_index('ix_realm_data_assets_owner_id', table_name='realm_data_assets')
    op.drop_index('ix_realm_data_assets_asset_key', table_name='realm_data_assets')
    op.drop_index('ix_realm_data_assets_project_id', table_name='realm_data_assets')
    op.drop_index('ix_realm_data_assets_entity_id', table_name='realm_data_assets')
    op.drop_table('realm_data_assets')
    op.drop_index('ix_geo_projects_realm_entity_id', table_name='geo_projects')
    op.drop_index('ix_geo_projects_realm_id', table_name='geo_projects')
    op.drop_index('ix_geo_projects_project_code', table_name='geo_projects')
    op.drop_table('geo_projects')
    op.drop_index('ix_realm_data_authorizations_owner_id', table_name='realm_data_authorizations')
    op.drop_index('ix_realm_data_authorizations_entity_id', table_name='realm_data_authorizations')
    op.drop_index('ix_realm_data_authorizations_authorization_code', table_name='realm_data_authorizations')
    op.drop_table('realm_data_authorizations')
    op.drop_index('ix_realm_claims_claimant_id', table_name='realm_claims')
    op.drop_index('ix_realm_claims_entity_id', table_name='realm_claims')
    op.drop_table('realm_claims')
    op.drop_index('ix_realm_registry_entity_id', table_name='realm_registry')
    op.drop_index('ix_realm_registry_owner_id', table_name='realm_registry')
    op.drop_index('ix_realm_registry_realm_code', table_name='realm_registry')
    op.drop_table('realm_registry')
