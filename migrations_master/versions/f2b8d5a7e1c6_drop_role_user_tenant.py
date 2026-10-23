"""drop role de user_tenant

Revision ID: f2b8d5a7e1c6
Revises: e6a9c3f1d8b4
Create Date: 2026-10-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2b8d5a7e1c6'
down_revision: Union[str, Sequence[str], None] = 'e6a9c3f1d8b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('user_tenant', 'role')


def downgrade() -> None:
    """Downgrade schema."""
    # Las filas existentes quedan con 'user': el rol original no se puede recuperar.
    op.add_column('user_tenant', sa.Column(
        'role',
        sa.Enum('control', 'user', 'viewer', 'employee', name='tenantrole'),
        server_default='user',
        nullable=False,
    ))
