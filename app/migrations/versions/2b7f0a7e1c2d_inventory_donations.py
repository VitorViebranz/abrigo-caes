"""Inventory and donations

Revision ID: 2b7f0a7e1c2d
Revises: 8f9b5a1c7d21
Create Date: 2026-05-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2b7f0a7e1c2d"
down_revision: Union[str, None] = "8f9b5a1c7d21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # cria o enum apenas se não existir (protege contra "type already exists")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'inventorymovementtype') THEN
                CREATE TYPE inventorymovementtype AS ENUM ('entrada','saida');
            END IF;
        END$$;
        """
    )

    inventory_movement_enum = sa.dialects.postgresql.ENUM(
        "entrada", "saida", name="inventorymovementtype", create_type=False
    )

    op.create_table(
        "inventory_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=300), nullable=True),
        sa.Column("unit", sa.String(length=30), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "inventory_movements",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("type", inventory_movement_enum, nullable=False),
        sa.Column("quantity", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("unit", sa.String(length=30), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("note", sa.String(length=300), nullable=True),
        sa.Column("reference", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["item_id"], ["inventory_items.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_inventory_movements_item_id"), "inventory_movements", ["item_id"], unique=False)

    op.create_table(
        "donations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("donor", sa.String(length=150), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("monetary_value", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("description", sa.String(length=300), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "donation_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("donation_id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("unit", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(["donation_id"], ["donations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["item_id"], ["inventory_items.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_donation_items_donation_id"), "donation_items", ["donation_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_donation_items_donation_id"), table_name="donation_items")
    op.drop_table("donation_items")
    op.drop_table("donations")
    op.drop_index(op.f("ix_inventory_movements_item_id"), table_name="inventory_movements")
    op.drop_table("inventory_movements")
    op.drop_table("inventory_items")

    # remove o enum somente se existir
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'inventorymovementtype') THEN
                DROP TYPE inventorymovementtype;
            END IF;
        END$$;
        """
    )
