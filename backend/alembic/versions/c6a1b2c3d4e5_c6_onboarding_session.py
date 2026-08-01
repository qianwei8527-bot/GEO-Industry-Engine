"""c6_onboarding_session

Revision ID: c6a1b2c3d4e5
Revises: 8a102209ac1e
Create Date: 2026-08-01 15:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'c6a1b2c3d4e5'
down_revision: Union[str, None] = '8a102209ac1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('onboarding_sessions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('idempotency_key', sa.String(length=128), nullable=False),
    sa.Column('session_status', sa.String(length=32), nullable=False),
    sa.Column('current_step', sa.Integer(), nullable=False),
    sa.Column('company_name', sa.String(length=255), nullable=True),
    sa.Column('data_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('activation_result_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('retry_count', sa.Integer(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_onboarding_sessions_idempotency_key'), 'onboarding_sessions', ['idempotency_key'], unique=True)

    op.add_column('evidence', sa.Column('source_name', sa.String(length=255), nullable=True))
    op.add_column('evidence', sa.Column('source_description', sa.Text(), nullable=True))
    op.add_column('evidence', sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('evidence', 'occurred_at')
    op.drop_column('evidence', 'source_description')
    op.drop_column('evidence', 'source_name')
    op.drop_index(op.f('ix_onboarding_sessions_idempotency_key'), table_name='onboarding_sessions')
    op.drop_table('onboarding_sessions')
