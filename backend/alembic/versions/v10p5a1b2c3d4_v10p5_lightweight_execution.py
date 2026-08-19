'''v10p5_lightweight_execution

Revision ID: v10p5a1b2c3d4
Revises: v10p1a1b2c3d4
Create Date: 2026-08-05
'''
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'v10p5a1b2c3d4'
down_revision: Union[str, None] = 'v10p1a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'client_intakes',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('intake_code', sa.String(length=64), nullable=False),
        sa.Column('realm_id', sa.UUID(), sa.ForeignKey('realm_registry.id', ondelete='CASCADE'), nullable=False),
        sa.Column('realm_entity_id', sa.UUID(), nullable=True),
        sa.Column('status', sa.String(length=24), nullable=False, server_default='uploaded'),
        sa.Column('relationship', sa.String(length=64), nullable=True),
        sa.Column('pasted_text', sa.Text(), nullable=True),
        sa.Column('supplemental_notes', sa.Text(), nullable=True),
        sa.Column('file_manifest', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('source_truth_status', sa.String(length=24), nullable=False, server_default='observed'),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('confirmed_by', sa.UUID(), nullable=True),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_client_intakes_intake_code', 'client_intakes', ['intake_code'], unique=True)
    op.create_index('ix_client_intakes_realm_id', 'client_intakes', ['realm_id'], unique=False)
    op.create_index('ix_client_intakes_realm_entity_id', 'client_intakes', ['realm_entity_id'], unique=False)

    op.create_table(
        'intake_analyses',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('intake_id', sa.UUID(), sa.ForeignKey('client_intakes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('realm_id', sa.UUID(), sa.ForeignKey('realm_registry.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', sa.String(length=24), nullable=False, server_default='draft'),
        sa.Column('analysis_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('suggested_next_steps', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('analysis_mode', sa.String(length=32), nullable=False, server_default='local_heuristic'),
        sa.Column('model_name', sa.String(length=128), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('confirmed_by', sa.UUID(), nullable=True),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_intake_analyses_intake_id', 'intake_analyses', ['intake_id'], unique=False)
    op.create_index('ix_intake_analyses_realm_id', 'intake_analyses', ['realm_id'], unique=False)

    op.create_table(
        'issue_records',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('issue_code', sa.String(length=64), nullable=False),
        sa.Column('realm_id', sa.UUID(), sa.ForeignKey('realm_registry.id', ondelete='CASCADE'), nullable=False),
        sa.Column('project_id', sa.UUID(), sa.ForeignKey('geo_projects.id', ondelete='SET NULL'), nullable=True),
        sa.Column('work_item_id', sa.UUID(), sa.ForeignKey('project_work_items.id', ondelete='SET NULL'), nullable=True),
        sa.Column('original_text', sa.Text(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('client_ref', sa.Text(), nullable=True),
        sa.Column('scenario', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=64), nullable=False, server_default='manual'),
        sa.Column('category', sa.String(length=64), nullable=True),
        sa.Column('severity', sa.String(length=16), nullable=False, server_default='normal'),
        sa.Column('status', sa.String(length=24), nullable=False, server_default='new'),
        sa.Column('possible_causes', sa.Text(), nullable=True),
        sa.Column('tried_methods', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('effective_methods', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ineffective_methods', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('final_solution', sa.Text(), nullable=True),
        sa.Column('evidence_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('applicability_boundary', sa.Text(), nullable=True),
        sa.Column('assignee_id', sa.UUID(), nullable=True),
        sa.Column('due_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('recurrence_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_template_candidate', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('template_status', sa.String(length=16), nullable=False, server_default='none'),
        sa.Column('ai_classification', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('resolved_by', sa.UUID(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('archived_by', sa.UUID(), nullable=True),
        sa.Column('archived_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_issue_records_issue_code', 'issue_records', ['issue_code'], unique=True)
    op.create_index('ix_issue_records_realm_id', 'issue_records', ['realm_id'], unique=False)
    op.create_index('ix_issue_records_project_id', 'issue_records', ['project_id'], unique=False)
    op.create_index('ix_issue_records_work_item_id', 'issue_records', ['work_item_id'], unique=False)
    op.create_index('ix_issue_records_category', 'issue_records', ['category'], unique=False)
    op.create_index('ix_issue_records_status', 'issue_records', ['status'], unique=False)

    op.create_table(
        'issue_events',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('issue_id', sa.UUID(), sa.ForeignKey('issue_records.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(length=32), nullable=False),
        sa.Column('actor_id', sa.UUID(), nullable=True),
        sa.Column('actor_label', sa.String(length=255), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_issue_events_issue_id', 'issue_events', ['issue_id'], unique=False)
    op.create_index('ix_issue_events_event_type', 'issue_events', ['event_type'], unique=False)

    work_item_columns = [
        ('phase', sa.String(length=64)),
        ('purpose', sa.Text()),
        ('reason', sa.Text()),
        ('owner_id', sa.UUID()),
        ('start_at', sa.DateTime(timezone=True)),
        ('due_at', sa.DateTime(timezone=True)),
        ('depends_on', postgresql.JSONB(astext_type=sa.Text())),
        ('acceptance_criteria', sa.Text()),
        ('required_materials', postgresql.JSONB(astext_type=sa.Text())),
        ('evidence_ids', postgresql.JSONB(astext_type=sa.Text())),
        ('risks', postgresql.JSONB(astext_type=sa.Text())),
        ('reminder_at', sa.DateTime(timezone=True)),
        ('execution_mode', sa.String(length=32)),
        ('completion_note', sa.Text()),
        ('last_synced_source', sa.String(length=64)),
        ('last_synced_at', sa.DateTime(timezone=True)),
    ]
    for name, column_type in work_item_columns:
        op.add_column('project_work_items', sa.Column(name, column_type, nullable=True))
    op.add_column('project_work_items', sa.Column('progress', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('project_work_items', 'progress')
    for name, _ in [
        ('phase', None), ('purpose', None), ('reason', None), ('owner_id', None),
        ('start_at', None), ('due_at', None), ('depends_on', None), ('acceptance_criteria', None),
        ('required_materials', None), ('evidence_ids', None), ('risks', None), ('reminder_at', None),
        ('execution_mode', None), ('completion_note', None), ('last_synced_source', None),
        ('last_synced_at', None),
    ]:
        op.drop_column('project_work_items', name)
    op.drop_index('ix_issue_events_event_type', table_name='issue_events')
    op.drop_index('ix_issue_events_issue_id', table_name='issue_events')
    op.drop_table('issue_events')
    op.drop_index('ix_issue_records_status', table_name='issue_records')
    op.drop_index('ix_issue_records_category', table_name='issue_records')
    op.drop_index('ix_issue_records_work_item_id', table_name='issue_records')
    op.drop_index('ix_issue_records_project_id', table_name='issue_records')
    op.drop_index('ix_issue_records_realm_id', table_name='issue_records')
    op.drop_index('ix_issue_records_issue_code', table_name='issue_records')
    op.drop_table('issue_records')
    op.drop_index('ix_intake_analyses_realm_id', table_name='intake_analyses')
    op.drop_index('ix_intake_analyses_intake_id', table_name='intake_analyses')
    op.drop_table('intake_analyses')
    op.drop_index('ix_client_intakes_realm_entity_id', table_name='client_intakes')
    op.drop_index('ix_client_intakes_realm_id', table_name='client_intakes')
    op.drop_index('ix_client_intakes_intake_code', table_name='client_intakes')
    op.drop_table('client_intakes')
