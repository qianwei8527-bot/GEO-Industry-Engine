"""v10p0r_hardening

Revision ID: v10p0ra1b2c3d4
Revises: v10p0b1b2c3d4
Create Date: 2026-08-03 12:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'v10p0ra1b2c3d4'
down_revision: Union[str, None] = 'v10p0b1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Realm identity and claims
    op.add_column('realm_claims', sa.Column('deduplication_hash', sa.String(length=64), nullable=True))
    op.add_column('realm_claims', sa.Column('decided_reason', sa.Text(), nullable=True))
    op.create_index('ix_realm_claims_deduplication_hash', 'realm_claims', ['deduplication_hash'], unique=True)
    op.create_check_constraint(
        'ck_realm_registry_realm_type',
        'realm_registry',
        "realm_type in ('enterprise', 'brand', 'product')",
    )

    # Execution-grade data authorization
    op.add_column('realm_data_authorizations', sa.Column('grantee_type', sa.String(length=24), nullable=True))
    op.add_column('realm_data_authorizations', sa.Column('grantee_id', sa.String(length=128), nullable=True))
    op.add_column('realm_data_authorizations', sa.Column('provider', sa.String(length=64), nullable=True))
    op.add_column('realm_data_authorizations', sa.Column('tool_name', sa.String(length=64), nullable=True))
    op.add_column('realm_data_authorizations', sa.Column('status', sa.String(length=16), nullable=False, server_default='active'))
    op.add_column('realm_data_authorizations', sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('realm_data_authorizations', sa.Column('revoked_by', sa.UUID(), nullable=True))
    op.add_column('realm_data_authorizations', sa.Column('revocation_reason', sa.Text(), nullable=True))
    op.add_column('realm_data_authorizations', sa.Column('sensitive_level', sa.String(length=24), nullable=False, server_default='none'))
    op.add_column('realm_data_authorizations', sa.Column('data_scope', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('realm_data_authorizations', sa.Column('allow_external_processing', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('realm_data_authorizations', sa.Column('allow_derived_content', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('realm_data_authorizations', sa.Column('retention_until', sa.DateTime(timezone=True), nullable=True))
    op.add_column('realm_data_authorizations', sa.Column('deletion_policy', sa.String(length=128), nullable=True))
    op.add_column('realm_data_authorizations', sa.Column('authorization_hash', sa.String(length=64), nullable=True))
    op.create_index('ix_realm_data_authorizations_status', 'realm_data_authorizations', ['status'], unique=False)
    op.create_index('ix_realm_data_authorizations_authorization_hash', 'realm_data_authorizations', ['authorization_hash'], unique=False)
    op.create_check_constraint(
        'ck_realm_data_authorization_real_metrics',
        'realm_data_authorizations',
        "(truth_status = 'verified' OR may_affect_real_metrics = false)",
    )

    # Tool execution audit chain
    op.add_column('tool_execution_records', sa.Column('realm_entity_id', sa.UUID(), nullable=True))
    op.add_column('tool_execution_records', sa.Column('authorization_id', sa.UUID(), nullable=True))
    op.add_column('tool_execution_records', sa.Column('authorization_hash', sa.String(length=64), nullable=True))
    op.add_column('tool_execution_records', sa.Column('input_manifest_hash', sa.String(length=64), nullable=True))
    op.add_column('tool_execution_records', sa.Column('output_manifest_hash', sa.String(length=64), nullable=True))
    op.add_column('tool_execution_records', sa.Column('execution_source', sa.String(length=24), nullable=False, server_default='declared'))
    op.create_foreign_key('fk_tool_execution_records_realm_id', 'tool_execution_records', 'realm_registry', ['realm_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_tool_execution_records_realm_entity_id', 'tool_execution_records', 'entities', ['realm_entity_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_tool_execution_records_authorization_id', 'tool_execution_records', 'realm_data_authorizations', ['authorization_id'], ['id'], ondelete='SET NULL')
    op.create_index('ix_tool_execution_records_realm_entity_id', 'tool_execution_records', ['realm_entity_id'], unique=False)
    op.create_index('ix_tool_execution_records_authorization_id', 'tool_execution_records', ['authorization_id'], unique=False)
    op.create_index('ix_tool_execution_records_execution_source', 'tool_execution_records', ['execution_source'], unique=False)

    # Project entity FK + outcome validation state
    op.create_foreign_key('fk_geo_projects_realm_entity_id', 'geo_projects', 'entities', ['realm_entity_id'], ['id'], ondelete='CASCADE')
    op.add_column('project_outcomes', sa.Column('validation_rule_version', sa.String(length=32), nullable=True))
    op.add_column('project_outcomes', sa.Column('validation_config_version', sa.String(length=32), nullable=True))
    op.add_column('project_outcomes', sa.Column('validation_config_hash', sa.String(length=64), nullable=True))
    op.add_column('project_outcomes', sa.Column('validation_reasons', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('project_outcomes', sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('project_outcomes', sa.Column('revoked_by', sa.UUID(), nullable=True))
    op.add_column('project_outcomes', sa.Column('revocation_reason', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('project_outcomes', 'revocation_reason')
    op.drop_column('project_outcomes', 'revoked_by')
    op.drop_column('project_outcomes', 'revoked_at')
    op.drop_column('project_outcomes', 'validation_reasons')
    op.drop_column('project_outcomes', 'validation_config_hash')
    op.drop_column('project_outcomes', 'validation_config_version')
    op.drop_column('project_outcomes', 'validation_rule_version')
    op.drop_constraint('fk_geo_projects_realm_entity_id', 'geo_projects', type_='foreignkey')

    op.drop_index('ix_tool_execution_records_execution_source', table_name='tool_execution_records')
    op.drop_index('ix_tool_execution_records_authorization_id', table_name='tool_execution_records')
    op.drop_index('ix_tool_execution_records_realm_entity_id', table_name='tool_execution_records')
    op.drop_constraint('fk_tool_execution_records_authorization_id', 'tool_execution_records', type_='foreignkey')
    op.drop_constraint('fk_tool_execution_records_realm_entity_id', 'tool_execution_records', type_='foreignkey')
    op.drop_constraint('fk_tool_execution_records_realm_id', 'tool_execution_records', type_='foreignkey')
    op.drop_column('tool_execution_records', 'execution_source')
    op.drop_column('tool_execution_records', 'output_manifest_hash')
    op.drop_column('tool_execution_records', 'input_manifest_hash')
    op.drop_column('tool_execution_records', 'authorization_hash')
    op.drop_column('tool_execution_records', 'authorization_id')
    op.drop_column('tool_execution_records', 'realm_entity_id')

    op.drop_index('ix_realm_data_authorizations_authorization_hash', table_name='realm_data_authorizations')
    op.drop_index('ix_realm_data_authorizations_status', table_name='realm_data_authorizations')
    op.drop_constraint('ck_realm_data_authorization_real_metrics', 'realm_data_authorizations', type_='check')
    op.drop_column('realm_data_authorizations', 'authorization_hash')
    op.drop_column('realm_data_authorizations', 'deletion_policy')
    op.drop_column('realm_data_authorizations', 'retention_until')
    op.drop_column('realm_data_authorizations', 'allow_derived_content')
    op.drop_column('realm_data_authorizations', 'allow_external_processing')
    op.drop_column('realm_data_authorizations', 'data_scope')
    op.drop_column('realm_data_authorizations', 'sensitive_level')
    op.drop_column('realm_data_authorizations', 'revocation_reason')
    op.drop_column('realm_data_authorizations', 'revoked_by')
    op.drop_column('realm_data_authorizations', 'revoked_at')
    op.drop_column('realm_data_authorizations', 'status')
    op.drop_column('realm_data_authorizations', 'tool_name')
    op.drop_column('realm_data_authorizations', 'provider')
    op.drop_column('realm_data_authorizations', 'grantee_id')
    op.drop_column('realm_data_authorizations', 'grantee_type')

    op.drop_constraint('ck_realm_registry_realm_type', 'realm_registry', type_='check')
    op.drop_index('ix_realm_claims_deduplication_hash', table_name='realm_claims')
    op.drop_column('realm_claims', 'decided_reason')
    op.drop_column('realm_claims', 'deduplication_hash')
