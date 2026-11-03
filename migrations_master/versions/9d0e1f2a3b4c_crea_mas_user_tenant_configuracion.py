"""crea mas_user_tenant_configuracion y le pasa codigo_operacion_fk y codigo_tercero_operacion_fk desde mas_user_tenant

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
    op.create_table(
        'mas_user_tenant_configuracion',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_tenant_id', sa.Integer(), nullable=False),
        sa.Column('codigo_operacion_fk', sa.String(length=20), nullable=True),
        sa.Column('codigo_tercero_operacion_fk', sa.Integer(), nullable=True),
        sa.Column('codigo_ciudad_origen_fk', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['user_tenant_id'], ['mas_user_tenant.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_tenant_id'),
    )
    # Conserva los valores ya cargados en mas_user_tenant antes de quitar las columnas
    op.execute(
        "INSERT INTO mas_user_tenant_configuracion (user_tenant_id, codigo_operacion_fk, codigo_tercero_operacion_fk) "
        "SELECT id, codigo_operacion_fk, codigo_tercero_operacion_fk FROM mas_user_tenant "
        "WHERE codigo_operacion_fk IS NOT NULL OR codigo_tercero_operacion_fk IS NOT NULL"
    )
    op.drop_column('mas_user_tenant', 'codigo_tercero_operacion_fk')
    op.drop_column('mas_user_tenant', 'codigo_operacion_fk')


def downgrade() -> None:
    op.add_column('mas_user_tenant', sa.Column('codigo_operacion_fk', sa.String(length=20), nullable=True))
    op.add_column('mas_user_tenant', sa.Column('codigo_tercero_operacion_fk', sa.Integer(), nullable=True))
    op.execute(
        "UPDATE mas_user_tenant ut JOIN mas_user_tenant_configuracion c ON c.user_tenant_id = ut.id "
        "SET ut.codigo_operacion_fk = c.codigo_operacion_fk, ut.codigo_tercero_operacion_fk = c.codigo_tercero_operacion_fk"
    )
    op.drop_table('mas_user_tenant_configuracion')
