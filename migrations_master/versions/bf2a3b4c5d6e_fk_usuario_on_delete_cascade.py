"""FKs a auth_user con ON DELETE CASCADE (eliminación de cuenta)

Revision ID: bf2a3b4c5d6e
Revises: ae1f2a3b4c5d
Create Date: 2026-11-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'bf2a3b4c5d6e'
down_revision: Union[str, Sequence[str], None] = 'ae1f2a3b4c5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLAS = ['auth_api_key', 'mas_credito_solicitud', 'mas_user_tenant', 'mas_tenant_despacho']


def _recrear_fk(tabla: str, ondelete: str | None) -> None:
    # El nombre del FK lo generó MySQL; se busca el real
    for fk in sa.inspect(op.get_bind()).get_foreign_keys(tabla):
        if fk['constrained_columns'] == ['usuario_id'] and fk['referred_table'] == 'auth_user':
            op.drop_constraint(fk['name'], tabla, type_='foreignkey')
    op.create_foreign_key(f'fk_{tabla}_usuario_id', tabla, 'auth_user', ['usuario_id'], ['id'], ondelete=ondelete)


def upgrade() -> None:
    for tabla in TABLAS:
        _recrear_fk(tabla, 'CASCADE')


def downgrade() -> None:
    for tabla in TABLAS:
        _recrear_fk(tabla, None)
