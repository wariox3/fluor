"""agrega empleado, cliente y cliente_id a mas_user_tenant

Revision ID: 7b8c9d0e1f2a
Revises: 6a7b8c9d0e1f
Create Date: 2026-11-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '7b8c9d0e1f2a'
down_revision: Union[str, Sequence[str], None] = '6a7b8c9d0e1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('mas_user_tenant', sa.Column('empleado', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('mas_user_tenant', sa.Column('cliente', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('mas_user_tenant', sa.Column('cliente_id', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('mas_user_tenant', 'cliente_id')
    op.drop_column('mas_user_tenant', 'cliente')
    op.drop_column('mas_user_tenant', 'empleado')
