"""inicial

Revision ID: 0a1b2c3d4e5f
Revises:
Create Date: 2026-10-22 00:00:00.000000

Migración inicial de la base master (reinicio del historial). Crea las tablas
de los módulos auth y mas tal como están en los modelos.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a1b2c3d4e5f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('mas_configuracion',
    sa.Column('codigo_configuracion_pk', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('tasa_interes', sa.Numeric(precision=5, scale=2), nullable=False),
    sa.PrimaryKeyConstraint('codigo_configuracion_pk')
    )
    op.create_index(op.f('ix_mas_configuracion_codigo_configuracion_pk'), 'mas_configuracion', ['codigo_configuracion_pk'], unique=False)
    op.create_table('mas_tenant',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=100), nullable=True),
    sa.Column('schema', sa.String(length=100), nullable=True),
    sa.Column('credito', sa.Boolean(), server_default='0', nullable=True),
    sa.Column('anticipo', sa.Boolean(), server_default='0', nullable=True),
    sa.Column('activo', sa.Boolean(), server_default='0', nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mas_tenant_id'), 'mas_tenant', ['id'], unique=False)
    op.create_table('auth_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=150), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('role', sa.Enum('admin', 'user', 'viewer', 'control', 'employee', name='userrole'), nullable=False),
    sa.Column('tenant_id', sa.Integer(), nullable=True),
    sa.Column('nombres', sa.String(length=150), nullable=True),
    sa.Column('apellidos', sa.String(length=150), nullable=True),
    sa.Column('numero_identificacion', sa.String(length=50), nullable=True),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('empleado_id', sa.Integer(), nullable=True),
    sa.Column('codigo_usuario_fk', sa.String(length=25), nullable=True),
    sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id'], ['mas_tenant.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_auth_user_email'), 'auth_user', ['email'], unique=True)
    op.create_index(op.f('ix_auth_user_id'), 'auth_user', ['id'], unique=False)
    op.create_table('auth_api_key',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('key_hash', sa.String(length=255), nullable=True),
    sa.Column('prefix', sa.String(length=20), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('tenant_id', sa.Integer(), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['tenant_id'], ['mas_tenant.id'], ),
    sa.ForeignKeyConstraint(['usuario_id'], ['auth_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_auth_api_key_key_hash'), 'auth_api_key', ['key_hash'], unique=True)
    op.create_table('auth_verificacion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=False),
    sa.Column('tipo', sa.Enum('registro', 'reenvio', 'recuperacion', name='tipoverificacion'), nullable=False),
    sa.Column('token', sa.String(length=64), nullable=False),
    sa.Column('estado', sa.Enum('pendiente', 'usado', name='estadoverificacion'), nullable=False),
    sa.Column('ip', sa.String(length=45), nullable=True),
    sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('fecha_uso', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['usuario_id'], ['auth_user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_auth_verificacion_id'), 'auth_verificacion', ['id'], unique=False)
    op.create_index(op.f('ix_auth_verificacion_token'), 'auth_verificacion', ['token'], unique=True)
    op.create_index(op.f('ix_auth_verificacion_usuario_id'), 'auth_verificacion', ['usuario_id'], unique=False)
    op.create_table('mas_credito_solicitud',
    sa.Column('codigo_credito_solicitud_pk', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=False),
    sa.Column('monto', sa.Numeric(precision=18, scale=2), nullable=False),
    sa.Column('plazo', sa.Integer(), nullable=False),
    sa.Column('tasa_interes', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('descripcion', sa.Text(), nullable=True),
    sa.Column('estado', sa.String(length=20), nullable=False),
    sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('fecha_actualizacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['usuario_id'], ['auth_user.id'], ),
    sa.PrimaryKeyConstraint('codigo_credito_solicitud_pk')
    )
    op.create_index(op.f('ix_mas_credito_solicitud_codigo_credito_solicitud_pk'), 'mas_credito_solicitud', ['codigo_credito_solicitud_pk'], unique=False)
    op.create_index(op.f('ix_mas_credito_solicitud_usuario_id'), 'mas_credito_solicitud', ['usuario_id'], unique=False)
    op.create_table('mas_invitacion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tenant_id', sa.Integer(), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=True),
    sa.Column('usuario_invitado_id', sa.Integer(), nullable=False),
    sa.Column('estado', sa.Enum('pendiente', 'aceptada', 'rechazada', 'cancelada', name='estadoinvitacion'), server_default='pendiente', nullable=False),
    sa.Column('fecha', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id'], ['mas_tenant.id'], ),
    sa.ForeignKeyConstraint(['usuario_id'], ['auth_user.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['usuario_invitado_id'], ['auth_user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mas_invitacion_tenant_id'), 'mas_invitacion', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_mas_invitacion_usuario_id'), 'mas_invitacion', ['usuario_id'], unique=False)
    op.create_index(op.f('ix_mas_invitacion_usuario_invitado_id'), 'mas_invitacion', ['usuario_invitado_id'], unique=False)
    op.create_table('mas_notificacion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=False),
    sa.Column('tipo', sa.String(length=50), nullable=False),
    sa.Column('titulo', sa.String(length=150), nullable=False),
    sa.Column('mensaje', sa.Text(), nullable=True),
    sa.Column('url', sa.String(length=255), nullable=True),
    sa.Column('leida', sa.Boolean(), server_default='0', nullable=False),
    sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['usuario_id'], ['auth_user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mas_notificacion_id'), 'mas_notificacion', ['id'], unique=False)
    op.create_index(op.f('ix_mas_notificacion_usuario_id'), 'mas_notificacion', ['usuario_id'], unique=False)
    op.create_table('mas_user_tenant',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=False),
    sa.Column('tenant_id', sa.Integer(), nullable=False),
    sa.Column('empleado_id', sa.Integer(), nullable=True),
    sa.Column('activo', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('control', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id'], ['mas_tenant.id'], ),
    sa.ForeignKeyConstraint(['usuario_id'], ['auth_user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('usuario_id', 'tenant_id', name='uq_user_tenant_usuario_tenant')
    )
    op.create_index(op.f('ix_mas_user_tenant_tenant_id'), 'mas_user_tenant', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_mas_user_tenant_usuario_id'), 'mas_user_tenant', ['usuario_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_mas_user_tenant_tenant_id'), table_name='mas_user_tenant')
    op.drop_index(op.f('ix_mas_user_tenant_usuario_id'), table_name='mas_user_tenant')
    op.drop_table('mas_user_tenant')
    op.drop_index(op.f('ix_mas_notificacion_id'), table_name='mas_notificacion')
    op.drop_index(op.f('ix_mas_notificacion_usuario_id'), table_name='mas_notificacion')
    op.drop_table('mas_notificacion')
    op.drop_index(op.f('ix_mas_invitacion_tenant_id'), table_name='mas_invitacion')
    op.drop_index(op.f('ix_mas_invitacion_usuario_id'), table_name='mas_invitacion')
    op.drop_index(op.f('ix_mas_invitacion_usuario_invitado_id'), table_name='mas_invitacion')
    op.drop_table('mas_invitacion')
    op.drop_index(op.f('ix_mas_credito_solicitud_codigo_credito_solicitud_pk'), table_name='mas_credito_solicitud')
    op.drop_index(op.f('ix_mas_credito_solicitud_usuario_id'), table_name='mas_credito_solicitud')
    op.drop_table('mas_credito_solicitud')
    op.drop_index(op.f('ix_auth_verificacion_id'), table_name='auth_verificacion')
    op.drop_index(op.f('ix_auth_verificacion_token'), table_name='auth_verificacion')
    op.drop_index(op.f('ix_auth_verificacion_usuario_id'), table_name='auth_verificacion')
    op.drop_table('auth_verificacion')
    op.drop_index(op.f('ix_auth_api_key_key_hash'), table_name='auth_api_key')
    op.drop_table('auth_api_key')
    op.drop_index(op.f('ix_auth_user_email'), table_name='auth_user')
    op.drop_index(op.f('ix_auth_user_id'), table_name='auth_user')
    op.drop_table('auth_user')
    op.drop_index(op.f('ix_mas_tenant_id'), table_name='mas_tenant')
    op.drop_table('mas_tenant')
    op.drop_index(op.f('ix_mas_configuracion_codigo_configuracion_pk'), table_name='mas_configuracion')
    op.drop_table('mas_configuracion')
