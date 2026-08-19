"""c6g20_world_version_snapshot

Revision ID: c6g20a1b2c3d4
Revises: c6g19a1b2c3d4
Create Date: 2026-08-02 01:30:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c6g20a1b2c3d4'
down_revision: Union[str, None] = 'c6g19a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('vertical_world_versions', sa.Column('world_name', sa.String(length=255), nullable=False, server_default=''))
    op.add_column('vertical_world_versions', sa.Column('world_description', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('vertical_world_versions', 'world_description')
    op.drop_column('vertical_world_versions', 'world_name')
