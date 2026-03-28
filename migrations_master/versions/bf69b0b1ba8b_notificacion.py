"""notificacion

Revision ID: bf69b0b1ba8b
Revises: 911da898445e
Create Date: 2026-03-28 08:44:01.797734

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'bf69b0b1ba8b'
down_revision: Union[str, Sequence[str], None] = '911da898445e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'notificacion',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('titulo', sa.String(length=150), nullable=False),
        sa.Column('mensaje', sa.Text(), nullable=True),
        sa.Column('url', sa.String(length=255), nullable=True),
        sa.Column('leida', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_notificacion_id'), 'notificacion', ['id'], unique=False)
    op.create_index(op.f('ix_notificacion_usuario_id'), 'notificacion', ['usuario_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_notificacion_usuario_id'), table_name='notificacion')
    op.drop_index(op.f('ix_notificacion_id'), table_name='notificacion')
    op.drop_table('notificacion')
