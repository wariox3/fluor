"""crea mas_tenant_despacho

Revision ID: 6a7b8c9d0e1f
Revises: 5f6a7b8c9d0e
Create Date: 2026-10-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '6a7b8c9d0e1f'
down_revision: Union[str, Sequence[str], None] = '5f6a7b8c9d0e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('mas_tenant_despacho',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fecha', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=False),
    sa.Column('tenant_id', sa.Integer(), nullable=False),
    sa.Column('codigo_despacho_fk', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['usuario_id'], ['auth_user.id'], ),
    sa.ForeignKeyConstraint(['tenant_id'], ['mas_tenant.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tenant_id', 'codigo_despacho_fk', name='uq_tenant_despacho_tenant_despacho')
    )
    op.create_index(op.f('ix_mas_tenant_despacho_usuario_id'), 'mas_tenant_despacho', ['usuario_id'], unique=False)
    op.create_index(op.f('ix_mas_tenant_despacho_tenant_id'), 'mas_tenant_despacho', ['tenant_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_mas_tenant_despacho_tenant_id'), table_name='mas_tenant_despacho')
    op.drop_index(op.f('ix_mas_tenant_despacho_usuario_id'), table_name='mas_tenant_despacho')
    op.drop_table('mas_tenant_despacho')
