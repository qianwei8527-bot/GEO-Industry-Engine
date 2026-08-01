"""c6g14_world_model_persistence

Revision ID: c6g14a1b2c3d4
Revises: c6g13a1b2c3d4
Create Date: 2026-08-01 23:55:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'c6g14a1b2c3d4'
down_revision: Union[str, None] = 'c6g13a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('knowledge_candidates', sa.Column('candidate_key', sa.String(length=255), nullable=True))
    op.add_column('knowledge_candidates', sa.Column('is_synthetic', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('knowledge_candidates', sa.Column('sources', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('knowledge_candidates', sa.Column('evidence_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('knowledge_candidates', sa.Column('observation_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('knowledge_candidates', sa.Column('proposal_id', sa.String(length=128), nullable=True))
    op.add_column('knowledge_candidates', sa.Column('adoption_record', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.create_index('ix_knowledge_candidates_candidate_key', 'knowledge_candidates', ['candidate_key'], unique=False)
    op.execute(
        "UPDATE knowledge_candidates SET candidate_key = "
        "concept_type || ':' || lower(concept_name) WHERE candidate_key IS NULL"
    )

    op.create_table('world_model_proposals',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('proposal_id', sa.String(length=128), nullable=False),
        sa.Column('candidate_id', sa.UUID(), nullable=True),
        sa.Column('candidate_key', sa.String(length=255), nullable=False),
        sa.Column('concept_name', sa.String(length=255), nullable=False),
        sa.Column('concept_type', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('ontology_suggestion', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('evidence_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('source_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('emergence_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('proposed_by', sa.String(length=128), nullable=False),
        sa.Column('reviewed_by', sa.String(length=128), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('law_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('law_explanation', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('correlation_id', sa.String(length=128), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('adopted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('registry_update_pending', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['candidate_id'], ['knowledge_candidates.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_world_model_proposals_proposal_id', 'world_model_proposals', ['proposal_id'], unique=True)
    op.create_index('ix_world_model_proposals_candidate_key', 'world_model_proposals', ['candidate_key'], unique=False)
    op.create_index('ix_world_model_proposals_status', 'world_model_proposals', ['status'], unique=False)
    op.create_index('ix_world_model_proposals_correlation_id', 'world_model_proposals', ['correlation_id'], unique=False)

    op.create_table('industry_contexts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('industry_id', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('emerging_concepts', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('proposals', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('evidence_links', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_industry_contexts_industry_id', 'industry_contexts', ['industry_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_industry_contexts_industry_id', table_name='industry_contexts')
    op.drop_table('industry_contexts')
    op.drop_index('ix_world_model_proposals_correlation_id', table_name='world_model_proposals')
    op.drop_index('ix_world_model_proposals_status', table_name='world_model_proposals')
    op.drop_index('ix_world_model_proposals_candidate_key', table_name='world_model_proposals')
    op.drop_index('ix_world_model_proposals_proposal_id', table_name='world_model_proposals')
    op.drop_table('world_model_proposals')
    op.drop_index('ix_knowledge_candidates_candidate_key', table_name='knowledge_candidates')
    op.drop_column('knowledge_candidates', 'adoption_record')
    op.drop_column('knowledge_candidates', 'proposal_id')
    op.drop_column('knowledge_candidates', 'observation_ids')
    op.drop_column('knowledge_candidates', 'evidence_ids')
    op.drop_column('knowledge_candidates', 'sources')
    op.drop_column('knowledge_candidates', 'is_synthetic')
    op.drop_column('knowledge_candidates', 'candidate_key')
