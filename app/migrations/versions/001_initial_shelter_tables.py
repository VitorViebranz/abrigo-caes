"""Initial shelter tables: users, dogs, vaccines, financial

Revision ID: 001_initial
Revises:
Create Date: 2026-01-01 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id",              sa.Integer(),     primary_key=True, autoincrement=True),
        sa.Column("full_name",       sa.String(255),   nullable=False),
        sa.Column("email",           sa.String(100),   nullable=False),
        sa.Column("hashed_password", sa.String(255),   nullable=False),
        sa.Column("is_active",       sa.Boolean(),     nullable=False, server_default="1"),
        sa.Column("role",            sa.Enum("admin", "funcionario", name="userrole"),
                                     nullable=False, server_default="funcionario"),
        sa.Column("created_at",      sa.DateTime(),    nullable=True),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "dogs",
        sa.Column("id",                    sa.Integer(),  primary_key=True, autoincrement=True),
        sa.Column("name",                  sa.String(100), nullable=False),
        sa.Column("estimated_age_months",  sa.Integer(),  nullable=False),
        sa.Column("size",                  sa.Enum("P", "M", "G", name="dogsize"), nullable=False),
        sa.Column("adoption_status",       sa.Enum("disponivel", "em_processo", "adotado",
                                                   name="adoptionstatus"),
                                           nullable=False, server_default="disponivel"),
        sa.Column("entry_date",            sa.Date(),     nullable=False),
        sa.Column("is_active",             sa.Boolean(),  nullable=False, server_default="1"),
        sa.Column("notes",                 sa.String(500), nullable=True),
        sa.Column("created_at",            sa.DateTime(), nullable=True),
        sa.Column("updated_at",            sa.DateTime(), nullable=True),
    )

    op.create_table(
        "vaccines",
        sa.Column("id",               sa.Integer(),  primary_key=True, autoincrement=True),
        sa.Column("dog_id",           sa.Integer(),  sa.ForeignKey("dogs.id", ondelete="CASCADE"),
                                      nullable=False),
        sa.Column("name",             sa.String(100), nullable=False),
        sa.Column("application_date", sa.Date(),     nullable=False),
        sa.Column("next_dose",        sa.Date(),     nullable=False),
        sa.Column("notes",            sa.String(300), nullable=True),
        sa.Column("created_at",       sa.DateTime(), nullable=True),
    )
    op.create_index("ix_vaccines_dog_id", "vaccines", ["dog_id"])

    op.create_table(
        "financial",
        sa.Column("id",          sa.Integer(),   primary_key=True, autoincrement=True),
        sa.Column("type",        sa.Enum("entrada", "saida", name="financialtype"), nullable=False),
        sa.Column("value",       sa.Numeric(10, 2), nullable=False),
        sa.Column("date",        sa.Date(),      nullable=False),
        sa.Column("category",    sa.Enum("doacao", "suprimentos", "veterinario",
                                         "custos_fixos", "outros", name="financialcategory"),
                                 nullable=False),
        sa.Column("description", sa.String(300), nullable=True),
        sa.Column("donor",       sa.String(150), nullable=True),
        sa.Column("is_active",   sa.Boolean(),   nullable=False, server_default="1"),
        sa.Column("created_at",  sa.DateTime(),  nullable=True),
    )


def downgrade() -> None:
    op.drop_table("financial")
    op.drop_index("ix_vaccines_dog_id", table_name="vaccines")
    op.drop_table("vaccines")
    op.drop_table("dogs")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
