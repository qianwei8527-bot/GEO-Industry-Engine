"""c6g07_user_role_reviewer

Revision ID: c6g07a1b2c3d4
Revises: c6g06a1b2c3d4
Create Date: 2026-08-01 19:30:00.000000
"""
from typing import Sequence, Union
from alembic import op

revision: str = 'c6g07a1b2c3d4'
down_revision: Union[str, None] = 'c6g06a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL enum type: add REVIEWER (idempotent-ish; if it exists, ignore error)
    try:
        op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'REVIEWER'")
    except Exception:
        pass


def downgrade() -> None:
    pass
