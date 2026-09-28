"""add is_active to user

Revision ID: e8a2b5d1f4c7
Revises: d7f3a1c9e2b4
Create Date: 2026-09-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8a2b5d1f4c7'
down_revision: Union[str, Sequence[str], None] = 'd7f3a1c9e2b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Se agrega con server_default = true: los usuarios existentes y cualquier
    # registro nuevo (incluso fuera de la app) quedan activos por defecto.
    op.add_column(
        'user',
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('user', 'is_active')
