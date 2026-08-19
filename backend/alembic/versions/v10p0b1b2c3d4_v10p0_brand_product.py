"""v10p0_brand_product

Revision ID: v10p0b1b2c3d4
Revises: v10p0a1b2c3d4
Create Date: 2026-08-03 10:05:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'v10p0b1b2c3d4'
down_revision: Union[str, None] = 'v10p0a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('brands',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['entities.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('products',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['entities.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('products')
    op.drop_table('brands')
