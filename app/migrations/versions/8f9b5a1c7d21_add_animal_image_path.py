"""Add animal image path

Revision ID: 8f9b5a1c7d21
Revises: eba5f264a5a5
Create Date: 2026-05-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8f9b5a1c7d21"
down_revision: Union[str, None] = "eba5f264a5a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("animals", sa.Column("image_path", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("animals", "image_path")
