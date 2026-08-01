"""c6g13_evidence_truth

Revision ID: c6g13a1b2c3d4
Revises: c6g12a1b2c3d4
Create Date: 2026-08-01 23:45:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c6g13a1b2c3d4'
down_revision: Union[str, None] = 'c6g12a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('evidence', sa.Column('truth_status', sa.String(length=24), nullable=False, server_default='observed'))
    op.add_column('evidence', sa.Column('is_synthetic', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('evidence', sa.Column('may_affect_real_metrics', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('evidence', sa.Column('source_record_id', sa.String(length=128), nullable=True))
    op.add_column('evidence', sa.Column('source_license', sa.String(length=255), nullable=True))
    op.add_column('evidence', sa.Column('content_hash', sa.String(length=64), nullable=True))
    op.add_column('evidence', sa.Column('excerpt', sa.Text(), nullable=True))
    op.add_column('evidence', sa.Column('retrieved_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('evidence', sa.Column('effective_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('evidence', sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('evidence', 'expires_at')
    op.drop_column('evidence', 'effective_at')
    op.drop_column('evidence', 'retrieved_at')
    op.drop_column('evidence', 'excerpt')
    op.drop_column('evidence', 'content_hash')
    op.drop_column('evidence', 'source_license')
    op.drop_column('evidence', 'source_record_id')
    op.drop_column('evidence', 'may_affect_real_metrics')
    op.drop_column('evidence', 'is_synthetic')
    op.drop_column('evidence', 'truth_status')
