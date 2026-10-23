"""add invitacion

Revision ID: e6a9c3f1d8b4
Revises: d4f7b2e9a5c3
Create Date: 2026-10-22 00:00:00.000000

Tabla de invitaciones a una empresa: usuario_id es quien invita y
usuario_invitado_id el invitado (usuario registrado y verificado).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6a9c3f1d8b4'
down_revision: Union[str, Sequence[str], None] = 'd4f7b2e9a5c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'invitacion',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.Column('usuario_invitado_id', sa.Integer(), nullable=False),
        sa.Column(
            'estado',
            sa.Enum('pendiente', 'aceptada', 'rechazada', 'cancelada', name='estadoinvitacion'),
            server_default='pendiente',
            nullable=False,
        ),
        sa.Column('fecha', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id'], name='fk_invitacion_tenant_id'),
        sa.ForeignKeyConstraint(['usuario_id'], ['user.id'], name='fk_invitacion_usuario_id', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['usuario_invitado_id'], ['user.id'], name='fk_invitacion_usuario_invitado_id', ondelete='CASCADE'),
    )
    op.create_index('ix_invitacion_tenant_id', 'invitacion', ['tenant_id'])
    op.create_index('ix_invitacion_usuario_id', 'invitacion', ['usuario_id'])
    op.create_index('ix_invitacion_usuario_invitado_id', 'invitacion', ['usuario_invitado_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_invitacion_usuario_invitado_id', table_name='invitacion')
    op.drop_index('ix_invitacion_usuario_id', table_name='invitacion')
    op.drop_index('ix_invitacion_tenant_id', table_name='invitacion')
    op.drop_table('invitacion')
