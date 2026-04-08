"""Init register default

Revision ID: 1349254e5117
Revises: 024d4599698a
Create Date: 2026-04-07 21:33:32.553597

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = '1349254e5117'
down_revision: Union[str, None] = '024d4599698a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('token', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('token_expires_at', sa.DateTime(), nullable=True))
    op.alter_column('users', 'full_name',
               existing_type=mysql.VARCHAR(length=255),
               type_=sa.String(length=100),
               existing_nullable=False)
    op.drop_index('uq_users_email', table_name='users')


def downgrade() -> None:
    op.create_index('uq_users_email', 'users', ['email'], unique=True)
    op.alter_column('users', 'full_name',
               existing_type=sa.String(length=100),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=False)
    op.drop_column('users', 'token_expires_at')
    op.drop_column('users', 'token')
