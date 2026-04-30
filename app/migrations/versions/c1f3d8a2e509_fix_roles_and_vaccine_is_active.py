"""Fix userrole enum and add is_active to vaccines

Revision ID: c1f3d8a2e509
Revises: bfab21f5afed
Create Date: 2026-04-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c1f3d8a2e509"
down_revision: Union[str, None] = "bfab21f5afed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Migrate existing 'funcionario' rows before altering the ENUM so MySQL
    # does not reject the conversion of unknown values.
    bind = op.get_bind()
    bind.execute(sa.text(
        "UPDATE users SET role = 'voluntario' WHERE role = 'funcionario'"
    ))

    # Alter the ENUM – MySQL requires MODIFY COLUMN for this.
    op.alter_column(
        "users",
        "role",
        existing_type=sa.Enum("admin", "funcionario", name="userrole"),
        type_=sa.Enum("admin", "voluntario", "financeiro", name="userrole"),
        existing_nullable=False,
        server_default="voluntario",
    )

    # Add is_active column to vaccines (default TRUE so existing rows stay active).
    op.add_column(
        "vaccines",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
    )


def downgrade() -> None:
    op.drop_column("vaccines", "is_active")

    bind = op.get_bind()
    # Revert voluntario/financeiro back to funcionario before shrinking the ENUM.
    bind.execute(sa.text(
        "UPDATE users SET role = 'funcionario' WHERE role IN ('voluntario', 'financeiro')"
    ))

    op.alter_column(
        "users",
        "role",
        existing_type=sa.Enum("admin", "voluntario", "financeiro", name="userrole"),
        type_=sa.Enum("admin", "funcionario", name="userrole"),
        existing_nullable=False,
        server_default="funcionario",
    )
