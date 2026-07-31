"""add_agent_memory

Revision ID: 67c88d1e3f5a
Revises: 64811ebba4a5
Create Date: 2026-07-29 14:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '67c88d1e3f5a'
down_revision: Union[str, None] = '64811ebba4a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'agent_memory',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('agent_name', sa.String(64), nullable=False, index=True),
        sa.Column('session_id', sa.String(64), nullable=False, index=True),
        sa.Column('task_id', sa.String(64), nullable=False),
        sa.Column('memory_type', sa.String(32), nullable=False, server_default='analysis'),
        sa.Column('key', sa.String(128), nullable=False),
        sa.Column('value', postgresql.JSONB, nullable=True),
        sa.Column('summary', sa.Text, nullable=True),
        sa.Column('citations', postgresql.JSONB, nullable=True),
        sa.Column('confidence', sa.Float, server_default='0.0'),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('tool_calls', postgresql.JSONB, nullable=True),
        sa.Column('step_index', sa.Integer, server_default='0'),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_agent_memory_session_agent', 'agent_memory', ['session_id', 'agent_name'])
    op.create_index('ix_agent_memory_entity', 'agent_memory', ['entity_id'])


def downgrade() -> None:
    op.drop_table('agent_memory')
