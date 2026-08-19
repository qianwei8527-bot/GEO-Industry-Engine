"""c6g15_trust_foundation

Revision ID: c6g15a1b2c3d4
Revises: c6g14a1b2c3d4
Create Date: 2026-08-01 23:59:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c6g15a1b2c3d4'
down_revision: Union[str, None] = 'c6g14a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('evidence', sa.Column('verification_method', sa.String(length=64), nullable=True))
    op.add_column('evidence', sa.Column('verification_result', sa.String(length=32), nullable=True))


def downgrade() -> None:
    op.drop_column('evidence', 'verification_result')
    op.drop_column('evidence', 'verification_method')
