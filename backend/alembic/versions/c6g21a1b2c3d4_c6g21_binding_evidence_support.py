"""c6g21_binding_evidence_support

Revision ID: c6g21a1b2c3d4
Revises: c6g20a1b2c3d4
Create Date: 2026-08-02 01:50:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'c6g21a1b2c3d4'
down_revision: Union[str, None] = 'c6g20a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('world_concepts', sa.Column('constraints', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.create_table('world_binding_evidence',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('binding_id', sa.UUID(), nullable=False),
        sa.Column('evidence_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['binding_id'], ['world_bindings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('binding_id', 'evidence_id', name='uq_binding_evidence'),
    )
    op.create_index('ix_world_binding_evidence_binding_id', 'world_binding_evidence', ['binding_id'], unique=False)
    op.create_index('ix_world_binding_evidence_evidence_id', 'world_binding_evidence', ['evidence_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_world_binding_evidence_evidence_id', table_name='world_binding_evidence')
    op.drop_index('ix_world_binding_evidence_binding_id', table_name='world_binding_evidence')
    op.drop_table('world_binding_evidence')
    op.drop_column('world_concepts', 'constraints')
