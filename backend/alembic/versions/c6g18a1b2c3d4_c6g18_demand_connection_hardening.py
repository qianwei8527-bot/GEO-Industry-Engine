"""c6g18_demand_connection_hardening

Revision ID: c6g18a1b2c3d4
Revises: c6g17a1b2c3d4
Create Date: 2026-08-02 00:50:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c6g18a1b2c3d4'
down_revision: Union[str, None] = 'c6g17a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('connection_candidates', sa.Column('decision_scope', sa.String(length=24), nullable=False, server_default='production'))
    op.add_column('connection_candidates', sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('connection_candidates', sa.Column('verified_evidence_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('connection_candidates', sa.Column('observed_evidence_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('connection_candidates', sa.Column('synthetic_evidence_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('connection_candidates', sa.Column('config_version', sa.String(length=32), nullable=False, server_default='1.0.0'))
    op.add_column('connection_candidates', sa.Column('config_hash', sa.String(length=64), nullable=True))
    op.create_unique_constraint(
        'uq_connection_candidates_demand_target_type',
        'connection_candidates',
        ['demand_event_id', 'target_node_id', 'connection_type'],
    )


def downgrade() -> None:
    op.drop_constraint('uq_connection_candidates_demand_target_type', 'connection_candidates', type_='unique')
    op.drop_column('connection_candidates', 'config_hash')
    op.drop_column('connection_candidates', 'config_version')
    op.drop_column('connection_candidates', 'synthetic_evidence_count')
    op.drop_column('connection_candidates', 'observed_evidence_count')
    op.drop_column('connection_candidates', 'verified_evidence_count')
    op.drop_column('connection_candidates', 'decided_at')
    op.drop_column('connection_candidates', 'decision_scope')
