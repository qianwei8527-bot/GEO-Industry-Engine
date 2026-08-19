"""c6g19_world_model_contract

Revision ID: c6g19a1b2c3d4
Revises: c6g18a1b2c3d4
Create Date: 2026-08-02 01:10:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'c6g19a1b2c3d4'
down_revision: Union[str, None] = 'c6g18a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('vertical_worlds',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=24), nullable=False, server_default='draft'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_vertical_worlds_code', 'vertical_worlds', ['code'], unique=True)

    op.create_table('vertical_world_versions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('world_id', sa.UUID(), nullable=False),
        sa.Column('version', sa.String(length=32), nullable=False),
        sa.Column('schema_version', sa.String(length=32), nullable=False, server_default='1.0'),
        sa.Column('config_hash', sa.String(length=64), nullable=False),
        sa.Column('source_file', sa.String(length=500), nullable=True),
        sa.Column('published_by', sa.String(length=128), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['world_id'], ['vertical_worlds.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('world_id', 'version', name='uq_world_version'),
    )

    op.create_table('world_concepts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('version_id', sa.UUID(), nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('concept_type', sa.String(length=32), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['version_id'], ['vertical_world_versions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('version_id', 'code', name='uq_world_concept_code'),
    )

    op.create_table('world_concept_relations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('version_id', sa.UUID(), nullable=False),
        sa.Column('relation_type', sa.String(length=32), nullable=False),
        sa.Column('from_concept', sa.String(length=64), nullable=False),
        sa.Column('to_concept', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['version_id'], ['vertical_world_versions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('version_id', 'from_concept', 'to_concept', 'relation_type', name='uq_world_relation'),
    )

    op.create_table('world_bindings',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('world_id', sa.UUID(), nullable=False),
        sa.Column('version_id', sa.UUID(), nullable=False),
        sa.Column('entity_type', sa.String(length=32), nullable=False),
        sa.Column('entity_id', sa.String(length=64), nullable=False),
        sa.Column('concept_code', sa.String(length=64), nullable=False),
        sa.Column('truth_status', sa.String(length=24), nullable=False, server_default='observed'),
        sa.Column('evidence_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('rule_version', sa.String(length=32), nullable=False, server_default='1.0.0'),
        sa.Column('mapping_source', sa.String(length=32), nullable=False, server_default='manual'),
        sa.Column('created_by', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['version_id'], ['vertical_world_versions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['world_id'], ['vertical_worlds.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('world_id', 'version_id', 'entity_type', 'entity_id', 'concept_code', name='uq_world_binding'),
    )
    op.create_index('ix_world_bindings_world_id', 'world_bindings', ['world_id'], unique=False)
    op.create_index('ix_world_bindings_version_id', 'world_bindings', ['version_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_world_bindings_version_id', table_name='world_bindings')
    op.drop_index('ix_world_bindings_world_id', table_name='world_bindings')
    op.drop_table('world_bindings')
    op.drop_table('world_concept_relations')
    op.drop_table('world_concepts')
    op.drop_table('vertical_world_versions')
    op.drop_index('ix_vertical_worlds_code', table_name='vertical_worlds')
    op.drop_table('vertical_worlds')
