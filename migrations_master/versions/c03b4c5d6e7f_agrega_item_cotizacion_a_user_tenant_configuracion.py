"""agrega ítem para cotizar a mas_user_tenant_configuracion

Revision ID: c03b4c5d6e7f
Revises: bf2a3b4c5d6e
Create Date: 2026-11-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c03b4c5d6e7f'
down_revision: Union[str, Sequence[str], None] = 'bf2a3b4c5d6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ítem de gen_item (base de la empresa, sin FK) con el que el usuario cotiza desde el portal
    op.add_column('mas_user_tenant_configuracion', sa.Column('codigo_item_cotizacion_fk', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('mas_user_tenant_configuracion', 'codigo_item_cotizacion_fk')
