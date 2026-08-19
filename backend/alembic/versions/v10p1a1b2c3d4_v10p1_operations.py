"""v10p1_operations

Revision ID: v10p1a1b2c3d4
Revises: v10p0ra1b2c3d4
Create Date: 2026-08-03 14:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'v10p1a1b2c3d4'
down_revision: Union[str, None] = 'v10p0ra1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('project_artifacts', sa.Column('published_url', sa.String(length=1000), nullable=True))
    op.add_column('project_artifacts', sa.Column('published_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('project_artifacts', sa.Column('published_by', sa.UUID(), nullable=True))
    op.add_column('project_artifacts', sa.Column('content_hash', sa.String(length=64), nullable=True))
    op.add_column('project_artifacts', sa.Column('delivery_recipient', sa.String(length=255), nullable=True))
    op.add_column('project_outcomes', sa.Column('observed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('project_outcomes', sa.Column('raw_result_ref', sa.String(length=1000), nullable=True))
    op.add_column('project_outcomes', sa.Column('metric_key', sa.String(length=128), nullable=True))
    op.add_column('project_outcomes', sa.Column('metric_value', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('project_outcomes', 'metric_value')
    op.drop_column('project_outcomes', 'metric_key')
    op.drop_column('project_outcomes', 'raw_result_ref')
    op.drop_column('project_outcomes', 'observed_at')
    op.drop_column('project_artifacts', 'delivery_recipient')
    op.drop_column('project_artifacts', 'content_hash')
    op.drop_column('project_artifacts', 'published_by')
    op.drop_column('project_artifacts', 'published_at')
    op.drop_column('project_artifacts', 'published_url')
