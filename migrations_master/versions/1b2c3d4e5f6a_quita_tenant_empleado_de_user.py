"""quita tenant_id y empleado_id de auth_user (pasan a mas_user_tenant)

Revision ID: 1b2c3d4e5f6a
Revises: 0a1b2c3d4e5f
Create Date: 2026-10-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '1b2c3d4e5f6a'
down_revision: Union[str, Sequence[str], None] = '0a1b2c3d4e5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # El FK de tenant_id no tiene nombre fijo (MySQL lo genera); se busca el real
    fks = sa.inspect(op.get_bind()).get_foreign_keys('auth_user')
    for fk in fks:
        if fk['constrained_columns'] == ['tenant_id']:
            op.drop_constraint(fk['name'], 'auth_user', type_='foreignkey')
    op.drop_column('auth_user', 'tenant_id')
    op.drop_column('auth_user', 'empleado_id')


def downgrade() -> None:
    op.add_column('auth_user', sa.Column('empleado_id', sa.Integer(), nullable=True))
    op.add_column('auth_user', sa.Column('tenant_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_auth_user_tenant_id', 'auth_user', 'mas_tenant', ['tenant_id'], ['id'])
