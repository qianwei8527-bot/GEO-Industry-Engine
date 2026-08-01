"""c6g06_change_audit

Revision ID: c6g06a1b2c3d4
Revises: c6g05a1b2c3d4
Create Date: 2026-08-01 19:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c6g06a1b2c3d4'
down_revision: Union[str, None] = 'c6g05a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('candidate_change_audits',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('change_id', sa.String(length=64), nullable=False),
    sa.Column('from_status', sa.String(length=32), nullable=False),
    sa.Column('to_status', sa.String(length=32), nullable=False),
    sa.Column('actor_id', sa.UUID(), nullable=True),
    sa.Column('reason', sa.Text(), nullable=True),
    sa.Column('request_id', sa.String(length=64), nullable=True),
    sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_candidate_change_audits_change_id', 'candidate_change_audits', ['change_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_candidate_change_audits_change_id', table_name='candidate_change_audits')
    op.drop_table('candidate_change_audits')
