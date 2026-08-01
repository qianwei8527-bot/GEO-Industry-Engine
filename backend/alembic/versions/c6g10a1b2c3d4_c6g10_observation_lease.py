"""c6g10_observation_lease

Revision ID: c6g10a1b2c3d4
Revises: c6g09a1b2c3d4
Create Date: 2026-08-01 22:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c6g10a1b2c3d4'
down_revision: Union[str, None] = 'c6g09a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('observation_sources', sa.Column('locked_by', sa.String(length=64), nullable=True))
    op.add_column('observation_sources', sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True))
    op.add_column('observation_sources', sa.Column('version', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('observation_sources', 'version')
    op.drop_column('observation_sources', 'locked_until')
    op.drop_column('observation_sources', 'locked_by')
