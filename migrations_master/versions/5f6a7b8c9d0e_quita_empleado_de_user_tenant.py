"""quita empleado de mas_user_tenant

Revision ID: 5f6a7b8c9d0e
Revises: 4e5f6a7b8c9d
Create Date: 2026-10-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '5f6a7b8c9d0e'
down_revision: Union[str, Sequence[str], None] = '4e5f6a7b8c9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('mas_user_tenant', 'empleado')


def downgrade() -> None:
    op.add_column('mas_user_tenant', sa.Column('empleado', sa.Boolean(), nullable=False, server_default=sa.false()))
