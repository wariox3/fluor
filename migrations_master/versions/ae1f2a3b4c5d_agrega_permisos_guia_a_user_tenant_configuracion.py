"""agrega permisos de guía a mas_user_tenant_configuracion

Revision ID: ae1f2a3b4c5d
Revises: 9d0e1f2a3b4c
Create Date: 2026-11-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'ae1f2a3b4c5d'
down_revision: Union[str, Sequence[str], None] = '9d0e1f2a3b4c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

COLUMNAS = [
    ('cambiar_valores_guia', False),
    ('permite_cambiar_adquiriente', False),
    ('estado_recogido', True),
    ('estado_ingreso', True),
    ('invertir_origen_destino', False),
    ('bloquear_recaudo', False),
    ('bloquear_adquiriente_credito', False),
    ('bloquear_operacion_cliente', False),
]


def upgrade() -> None:
    # server_default llena las filas existentes con el valor por defecto
    for nombre, defecto in COLUMNAS:
        op.add_column('mas_user_tenant_configuracion', sa.Column(
            nombre, sa.Boolean(), nullable=False, server_default=sa.true() if defecto else sa.false()))


def downgrade() -> None:
    for nombre, _ in reversed(COLUMNAS):
        op.drop_column('mas_user_tenant_configuracion', nombre)
