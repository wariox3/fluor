"""agrega codigo_ciudad_origen_fk a mas_user_tenant_configuracion

Revision ID: 9d0e1f2a3b4c
Revises: 8c9d0e1f2a3b
Create Date: 2026-11-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9d0e1f2a3b4c'
down_revision: Union[str, Sequence[str], None] = '8c9d0e1f2a3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('mas_user_tenant_configuracion', sa.Column('codigo_ciudad_origen_fk', sa.String(length=20), nullable=True))


def downgrade() -> None:
    op.drop_column('mas_user_tenant_configuracion', 'codigo_ciudad_origen_fk')
