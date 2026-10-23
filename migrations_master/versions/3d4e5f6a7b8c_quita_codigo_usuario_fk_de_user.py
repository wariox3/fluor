"""quita codigo_usuario_fk de auth_user (pasa a mas_user_tenant)

Revision ID: 3d4e5f6a7b8c
Revises: 2c3d4e5f6a7b
Create Date: 2026-10-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '3d4e5f6a7b8c'
down_revision: Union[str, Sequence[str], None] = '2c3d4e5f6a7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('auth_user', 'codigo_usuario_fk')


def downgrade() -> None:
    op.add_column('auth_user', sa.Column('codigo_usuario_fk', sa.String(length=25), nullable=True))
