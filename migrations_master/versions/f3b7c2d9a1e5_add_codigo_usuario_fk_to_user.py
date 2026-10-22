"""add codigo_usuario_fk to user

Revision ID: f3b7c2d9a1e5
Revises: e8a2b5d1f4c7
Create Date: 2026-10-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3b7c2d9a1e5'
down_revision: Union[str, Sequence[str], None] = 'e8a2b5d1f4c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('user', sa.Column('codigo_usuario_fk', sa.String(length=25), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('user', 'codigo_usuario_fk')
