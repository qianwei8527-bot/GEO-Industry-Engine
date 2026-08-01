"""c6g12_answer_origin

Revision ID: c6g12a1b2c3d4
Revises: c6g11a1b2c3d4
Create Date: 2026-08-01 23:30:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c6g12a1b2c3d4'
down_revision: Union[str, None] = 'c6g11a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('ai_answer_artifacts', sa.Column('data_origin', sa.String(length=16), nullable=False, server_default='fake'))
    op.add_column('ai_answer_artifacts', sa.Column('observation_mode', sa.String(length=24), nullable=False, server_default='unknown'))
    op.add_column('ai_answer_artifacts', sa.Column('baseline_eligible', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('ai_answer_artifacts', sa.Column('provider_verified', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    op.drop_column('ai_answer_artifacts', 'provider_verified')
    op.drop_column('ai_answer_artifacts', 'baseline_eligible')
    op.drop_column('ai_answer_artifacts', 'observation_mode')
    op.drop_column('ai_answer_artifacts', 'data_origin')
