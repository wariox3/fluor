"""crea mas_user_tenant_configuracion

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
    op.create_table(
        'mas_user_tenant_configuracion',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_tenant_id', sa.Integer(), nullable=False),
        sa.Column('codigo_operacion_fk', sa.String(length=20), nullable=True),
        sa.Column('codigo_tercero_operacion_fk', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_tenant_id'], ['mas_user_tenant.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_tenant_id'),
    )


def downgrade() -> None:
    op.drop_table('mas_user_tenant_configuracion')
