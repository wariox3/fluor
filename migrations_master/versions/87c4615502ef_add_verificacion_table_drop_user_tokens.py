"""add verificacion table, drop user tokens

Revision ID: 87c4615502ef
Revises: c2a5e8bf8571
Create Date: 2026-06-16 09:51:39.719811

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '87c4615502ef'
down_revision: Union[str, Sequence[str], None] = 'c2a5e8bf8571'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'verificacion',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('tipo', sa.Enum('registro', 'reenvio', 'recuperacion', name='tipoverificacion'), nullable=False),
        sa.Column('token', sa.String(length=64), nullable=False),
        sa.Column('estado', sa.Enum('pendiente', 'usado', name='estadoverificacion'), nullable=False),
        sa.Column('ip', sa.String(length=45), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
        sa.Column('fecha_uso', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['usuario_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_verificacion_id'), 'verificacion', ['id'], unique=False)
    op.create_index(op.f('ix_verificacion_usuario_id'), 'verificacion', ['usuario_id'], unique=False)
    op.create_index(op.f('ix_verificacion_token'), 'verificacion', ['token'], unique=True)

    op.drop_index(op.f('ix_user_reset_password_token'), table_name='user')
    op.drop_index(op.f('ix_user_verification_token'), table_name='user')
    op.drop_column('user', 'reset_password_token')
    op.drop_column('user', 'verification_token')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('user', sa.Column('verification_token', mysql.VARCHAR(length=64), nullable=True))
    op.add_column('user', sa.Column('reset_password_token', mysql.VARCHAR(length=64), nullable=True))
    op.create_index(op.f('ix_user_verification_token'), 'user', ['verification_token'], unique=True)
    op.create_index(op.f('ix_user_reset_password_token'), 'user', ['reset_password_token'], unique=True)

    # drop_table elimina índices y la FK asociada (no se pueden borrar antes
    # porque MySQL exige el índice mientras exista la foreign key).
    op.drop_table('verificacion')
