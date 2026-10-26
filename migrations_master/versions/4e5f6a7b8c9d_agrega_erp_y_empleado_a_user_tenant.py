"""agrega erp y empleado a mas_user_tenant

Revision ID: 4e5f6a7b8c9d
Revises: 3d4e5f6a7b8c
Create Date: 2026-10-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '4e5f6a7b8c9d'
down_revision: Union[str, Sequence[str], None] = '3d4e5f6a7b8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('mas_user_tenant', sa.Column('erp', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('mas_user_tenant', sa.Column('empleado', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column('mas_user_tenant', 'empleado')
    op.drop_column('mas_user_tenant', 'erp')
