"""add user_tenant

Revision ID: b5d8e1a4c7f2
Revises: f3b7c2d9a1e5
Create Date: 2026-10-22 00:00:00.000000

Crea la tabla intermedia usuario–empresa. Solo estructura: la copia de los
accesos actuales (user.tenant_id, role, empleado_id) se hace manualmente.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5d8e1a4c7f2'
down_revision: Union[str, Sequence[str], None] = 'f3b7c2d9a1e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'user_tenant',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenant.id'), nullable=False),
        sa.Column('role', sa.Enum('control', 'user', 'viewer', 'employee', name='tenantrole'), nullable=False),
        sa.Column('empleado_id', sa.Integer(), nullable=True),
        sa.Column('activo', sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('usuario_id', 'tenant_id', name='uq_user_tenant_usuario_tenant'),
    )
    op.create_index('ix_user_tenant_usuario_id', 'user_tenant', ['usuario_id'])
    op.create_index('ix_user_tenant_tenant_id', 'user_tenant', ['tenant_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_user_tenant_tenant_id', table_name='user_tenant')
    op.drop_index('ix_user_tenant_usuario_id', table_name='user_tenant')
    op.drop_table('user_tenant')
