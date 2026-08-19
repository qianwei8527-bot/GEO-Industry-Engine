"""c6g22_evidence_claim

Revision ID: c6g22a1b2c3d4
Revises: c6g21a1b2c3d4
Create Date: 2026-08-02 02:10:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'c6g22a1b2c3d4'
down_revision: Union[str, None] = 'c6g21a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('evidence_claims',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('evidence_id', sa.UUID(), nullable=False),
        sa.Column('subject_type', sa.String(length=32), nullable=False),
        sa.Column('subject_id', sa.String(length=64), nullable=False),
        sa.Column('predicate_code', sa.String(length=64), nullable=False),
        sa.Column('object_type', sa.String(length=32), nullable=False),
        sa.Column('object_code', sa.String(length=64), nullable=False),
        sa.Column('object_value', sa.String(length=500), nullable=True),
        sa.Column('claim_text', sa.Text(), nullable=False),
        sa.Column('source_locator', sa.String(length=1000), nullable=True),
        sa.Column('extraction_method', sa.String(length=32), nullable=False, server_default='structured'),
        sa.Column('truth_status', sa.String(length=24), nullable=False, server_default='observed'),
        sa.Column('verification_method', sa.String(length=64), nullable=True),
        sa.Column('verification_result', sa.String(length=32), nullable=True),
        sa.Column('verified_by', sa.String(length=128), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('valid_from', sa.DateTime(timezone=True), nullable=True),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('may_affect_real_metrics', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('claim_hash', sa.String(length=64), nullable=False),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['evidence_id'], ['evidence.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_evidence_claims_evidence_id', 'evidence_claims', ['evidence_id'], unique=False)
    op.create_index('ix_evidence_claims_subject_id', 'evidence_claims', ['subject_id'], unique=False)
    op.create_index('ix_evidence_claims_predicate_code', 'evidence_claims', ['predicate_code'], unique=False)
    op.create_index('ix_evidence_claims_object_code', 'evidence_claims', ['object_code'], unique=False)
    op.create_index('ix_evidence_claims_claim_hash', 'evidence_claims', ['claim_hash'], unique=False)
    op.add_column('world_binding_evidence', sa.Column('evidence_claim_id', sa.UUID(), nullable=True))
    op.create_index('ix_world_binding_evidence_evidence_claim_id', 'world_binding_evidence', ['evidence_claim_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_world_binding_evidence_evidence_claim_id', table_name='world_binding_evidence')
    op.drop_column('world_binding_evidence', 'evidence_claim_id')
    op.drop_index('ix_evidence_claims_claim_hash', table_name='evidence_claims')
    op.drop_index('ix_evidence_claims_object_code', table_name='evidence_claims')
    op.drop_index('ix_evidence_claims_predicate_code', table_name='evidence_claims')
    op.drop_index('ix_evidence_claims_subject_id', table_name='evidence_claims')
    op.drop_index('ix_evidence_claims_evidence_id', table_name='evidence_claims')
    op.drop_table('evidence_claims')
