"""Seed initial admin user

Revision ID: 002_seed_admin
Revises: 001_initial
Create Date: 2026-01-01 00:01:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002_seed_admin"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from datetime import datetime, timezone
    import bcrypt

    hashed = bcrypt.hashpw(b"Admin@abrigo2025", bcrypt.gensalt()).decode("utf-8")

    op.bulk_insert(
        sa.table(
            "users",
            sa.column("full_name",       sa.String),
            sa.column("email",           sa.String),
            sa.column("hashed_password", sa.String),
            sa.column("is_active",       sa.Boolean),
            sa.column("role",            sa.String),
            sa.column("created_at",      sa.DateTime),
        ),
        [{
            "full_name":       "Administrador",
            "email":           "admin@abrigo.com",
            "hashed_password": hashed,
            "is_active":       True,
            "role":            "admin",
            "created_at":      datetime.now(timezone.utc),
        }],
    )


def downgrade() -> None:
    op.execute("DELETE FROM users WHERE email = 'admin@abrigo.com'")
