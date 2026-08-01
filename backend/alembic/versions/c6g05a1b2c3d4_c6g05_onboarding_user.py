"""c6g05_onboarding_user

Revision ID: c6g05a1b2c3d4
Revises: c6g04a1b2c3d4
Create Date: 2026-08-01 18:30:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c6g05a1b2c3d4'
down_revision: Union[str, None] = 'c6g04a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('onboarding_sessions', sa.Column('user_id', sa.UUID(), nullable=True))
    op.create_index('ix_onboarding_sessions_user_id', 'onboarding_sessions', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_onboarding_sessions_user_id', table_name='onboarding_sessions')
    op.drop_column('onboarding_sessions', 'user_id')
