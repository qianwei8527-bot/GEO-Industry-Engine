"""v10p7_qianwei_account

Revision ID: v10p7a1b2c3d4
Revises: v10p6a1b2c3d4
Create Date: 2026-08-07 14:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'v10p7a1b2c3d4'
down_revision: Union[str, None] = 'v10p6a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('username', sa.String(length=64), nullable=True))
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.execute(sa.text("""
        INSERT INTO users (id, email, username, password_hash, name, role, is_active, created_at, updated_at)
        VALUES (
            '00000000-0000-0000-0000-000000000001',
            'qianwei@universe.local',
            'qianwei',
            '$2b$12$pbCv7cnXKsE3R7K3vJq.P.Jo66Sdxjkohvi3HoPSUlV1jb1OI2nf2',
            'qianwei',
            'ADMIN',
            true,
            now(),
            now()
        )
        ON CONFLICT (email) DO UPDATE SET
            username = EXCLUDED.username,
            password_hash = EXCLUDED.password_hash,
            role = EXCLUDED.role,
            is_active = true
    """))


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM users WHERE username = 'qianwei'"))
    op.drop_index('ix_users_username', table_name='users')
    op.drop_column('users', 'username')
