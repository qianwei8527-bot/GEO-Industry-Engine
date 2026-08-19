"""v10p6_capability_module

Revision ID: v10p6a1b2c3d4
Revises: v10p5a1b2c3d4
Create Date: 2026-08-07 12:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'v10p6a1b2c3d4'
down_revision: Union[str, None] = 'v10p5a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'capability_definitions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('capability_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('capability_type', sa.String(length=32), nullable=False),
        sa.Column('source_mode', sa.String(length=24), nullable=False),
        sa.Column('status', sa.String(length=24), nullable=False),
        sa.Column('publisher', sa.String(length=255), nullable=True),
        sa.Column('owner_id', sa.UUID(), nullable=True),
        sa.Column('realm_entity_id', sa.UUID(), nullable=True),
        sa.Column('provider', sa.String(length=64), nullable=True),
        sa.Column('tool_name', sa.String(length=64), nullable=True),
        sa.Column('model_name', sa.String(length=128), nullable=True),
        sa.Column('model_version', sa.String(length=64), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('input_schema', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('output_schema', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('required_authorization_scope', sa.String(length=64), nullable=True),
        sa.Column('allow_external_processing', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('data_destination', sa.String(length=255), nullable=True),
        sa.Column('config_version', sa.String(length=32), nullable=False, server_default='1.0.0'),
        sa.Column('config_hash', sa.String(length=64), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['realm_entity_id'], ['entities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('capability_id'),
    )
    op.create_index('ix_capability_definitions_capability_id', 'capability_definitions', ['capability_id'], unique=True)
    op.create_index('ix_capability_definitions_capability_type', 'capability_definitions', ['capability_type'], unique=False)
    op.create_index('ix_capability_definitions_source_mode', 'capability_definitions', ['source_mode'], unique=False)
    op.create_index('ix_capability_definitions_owner_id', 'capability_definitions', ['owner_id'], unique=False)
    op.create_index('ix_capability_definitions_realm_entity_id', 'capability_definitions', ['realm_entity_id'], unique=False)

    op.add_column('tool_execution_records', sa.Column('capability_id', sa.String(length=64), nullable=True))
    op.add_column('tool_execution_records', sa.Column('capability_version', sa.String(length=32), nullable=True))
    op.add_column('tool_execution_records', sa.Column('capability_type', sa.String(length=32), nullable=True))
    op.add_column('tool_execution_records', sa.Column('source_mode', sa.String(length=24), nullable=False, server_default='platform_standard'))
    op.create_index('ix_tool_execution_records_capability_id', 'tool_execution_records', ['capability_id'], unique=False)
    op.create_index('ix_tool_execution_records_capability_type', 'tool_execution_records', ['capability_type'], unique=False)
    op.create_index('ix_tool_execution_records_source_mode', 'tool_execution_records', ['source_mode'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_tool_execution_records_source_mode', table_name='tool_execution_records')
    op.drop_index('ix_tool_execution_records_capability_type', table_name='tool_execution_records')
    op.drop_index('ix_tool_execution_records_capability_id', table_name='tool_execution_records')
    op.drop_column('tool_execution_records', 'source_mode')
    op.drop_column('tool_execution_records', 'capability_type')
    op.drop_column('tool_execution_records', 'capability_version')
    op.drop_column('tool_execution_records', 'capability_id')
    op.drop_index('ix_capability_definitions_realm_entity_id', table_name='capability_definitions')
    op.drop_index('ix_capability_definitions_owner_id', table_name='capability_definitions')
    op.drop_index('ix_capability_definitions_source_mode', table_name='capability_definitions')
    op.drop_index('ix_capability_definitions_capability_type', table_name='capability_definitions')
    op.drop_index('ix_capability_definitions_capability_id', table_name='capability_definitions')
    op.drop_table('capability_definitions')
