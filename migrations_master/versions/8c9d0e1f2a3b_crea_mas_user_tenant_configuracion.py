"""agrega codigo_operacion_fk y codigo_tercero_operacion_fk a mas_user_tenant

Revision ID: 8c9d0e1f2a3b
Revises: 7b8c9d0e1f2a
Create Date: 2026-11-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '8c9d0e1f2a3b'
down_revision: Union[str, Sequence[str], None] = '7b8c9d0e1f2a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('mas_user_tenant', sa.Column('codigo_operacion_fk', sa.String(length=20), nullable=True))
    op.add_column('mas_user_tenant', sa.Column('codigo_tercero_operacion_fk', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('mas_user_tenant', 'codigo_tercero_operacion_fk')
    op.drop_column('mas_user_tenant', 'codigo_operacion_fk')
