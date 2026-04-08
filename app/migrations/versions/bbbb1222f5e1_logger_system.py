"""Logger System

Revision ID: bbbb1222f5e1
Revises: 1349254e5117
Create Date: 2026-04-07 22:27:50.691273

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'bbbb1222f5e1'
down_revision: Union[str, None] = '1349254e5117'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('system_logs',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('trace_id', sa.String(length=36), nullable=True),
    sa.Column('level', sa.String(length=20), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('route', sa.String(length=255), nullable=True),
    sa.Column('method', sa.String(length=10), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_logs_trace_id'), 'system_logs', ['trace_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_system_logs_trace_id'), table_name='system_logs')
    op.drop_table('system_logs')