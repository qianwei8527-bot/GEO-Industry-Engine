"""GEO-Industry-Engine Sprint 1: 补全缺失字段

Revision ID: 003
Revises: 002
Create Date: 2026-07-28
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # trust table
    op.create_table(
        "trust",
        sa.Column("id", postgresql.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("entity_id", postgresql.UUID(), nullable=False),
        sa.Column("entity_type", sa.String(32), nullable=False),
        sa.Column("trust_score", sa.Float(), default=0.0),
        sa.Column("evidence_count", sa.Integer(), default=0),
        sa.Column("certification_level", sa.String(10), default="L0"),
        sa.Column("last_evaluated_at", sa.DateTime(timezone=True)),
        sa.Column("tenant_id", postgresql.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # companies new fields
    for col_name, col_type in [
        ("founded_year", sa.Integer()),
        ("headquarters", sa.String(255)),
        ("employee_count", sa.Integer()),
        ("annual_revenue", sa.String(50)),
        ("business_scope", sa.Text()),
    ]:
        try:
            op.add_column("companies", sa.Column(col_name, col_type, nullable=True))
        except Exception:
            pass

    op.create_index("ix_trust_entity", "trust", ["entity_id"])


def downgrade() -> None:
    op.drop_index("ix_trust_entity", table_name="trust")
    for col_name in ["business_scope", "annual_revenue", "employee_count", "headquarters", "founded_year"]:
        try:
            op.drop_column("companies", col_name)
        except Exception:
            pass
    op.drop_table("trust")
