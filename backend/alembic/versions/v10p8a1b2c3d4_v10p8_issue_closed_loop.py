"""v10p8_issue_closed_loop

Revision ID: v10p8a1b2c3d4
Revises: v10p7a1b2c3d4
Create Date: 2026-08-17 18:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "v10p8a1b2c3d4"
down_revision: Union[str, None] = "v10p7a1b2c3d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("issue_records", sa.Column("impact", sa.Text(), nullable=True))
    op.add_column("issue_records", sa.Column("urgency", sa.String(length=16), nullable=True))
    op.add_column("issue_records", sa.Column("source_type", sa.String(length=32), nullable=False, server_default="owner_manual"))
    op.add_column("issue_records", sa.Column("truth_scope", sa.String(length=24), nullable=False, server_default="observed"))
    op.add_column("issue_records", sa.Column("version", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("issue_records", sa.Column("idempotency_key", sa.String(length=128), nullable=True))
    op.add_column("issue_records", sa.Column("classification_status", sa.String(length=24), nullable=False, server_default="suggested"))
    op.add_column("issue_records", sa.Column("verified_by", sa.UUID(), nullable=True))
    op.add_column("issue_records", sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_issue_records_idempotency_key", "issue_records", ["idempotency_key"], unique=True)
    op.add_column("issue_events", sa.Column("event_version", sa.Integer(), nullable=False, server_default="1"))
    op.execute(sa.text("""
        UPDATE issue_events e
        SET event_version = sub.rn
        FROM (
            SELECT id, ROW_NUMBER() OVER (PARTITION BY issue_id ORDER BY created_at, id) AS rn
            FROM issue_events
        ) sub
        WHERE e.id = sub.id
    """))
    op.create_unique_constraint("uq_issue_event_version", "issue_events", ["issue_id", "event_version"])


def downgrade() -> None:
    op.drop_constraint("uq_issue_event_version", "issue_events", type_="unique")
    op.drop_column("issue_events", "event_version")
    op.drop_index("ix_issue_records_idempotency_key", table_name="issue_records")
    op.drop_column("issue_records", "verified_at")
    op.drop_column("issue_records", "verified_by")
    op.drop_column("issue_records", "classification_status")
    op.drop_column("issue_records", "idempotency_key")
    op.drop_column("issue_records", "version")
    op.drop_column("issue_records", "truth_scope")
    op.drop_column("issue_records", "source_type")
    op.drop_column("issue_records", "urgency")
    op.drop_column("issue_records", "impact")
