"""agrega codigo_usuario_fk a mas_user_tenant

Revision ID: 2c3d4e5f6a7b
Revises: 1b2c3d4e5f6a
Create Date: 2026-10-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '2c3d4e5f6a7b'
down_revision: Union[str, Sequence[str], None] = '1b2c3d4e5f6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('mas_user_tenant', sa.Column('codigo_usuario_fk', sa.String(length=25), nullable=True))


def downgrade() -> None:
    op.drop_column('mas_user_tenant', 'codigo_usuario_fk')
