"""notificacion

Revision ID: bf69b0b1ba8b
Revises: 911da898445e
Create Date: 2026-03-28 08:44:01.797734

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'bf69b0b1ba8b'
down_revision: Union[str, Sequence[str], None] = '911da898445e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table('auth_notificacion', 'notificacion')


def downgrade() -> None:
    op.rename_table('notificacion', 'auth_notificacion')
