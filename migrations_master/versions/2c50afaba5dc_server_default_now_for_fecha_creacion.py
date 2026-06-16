"""server_default now for fecha_creacion

Revision ID: 2c50afaba5dc
Revises: 87c4615502ef
Create Date: 2026-06-16 11:58:06.869750

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c50afaba5dc'
down_revision: Union[str, Sequence[str], None] = '87c4615502ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'user', 'fecha_creacion',
        existing_type=sa.DateTime(), existing_nullable=False,
        server_default=sa.text('CURRENT_TIMESTAMP'),
    )
    op.alter_column(
        'verificacion', 'fecha_creacion',
        existing_type=sa.DateTime(), existing_nullable=False,
        server_default=sa.text('CURRENT_TIMESTAMP'),
    )
    op.alter_column(
        'notificacion', 'fecha_creacion',
        existing_type=sa.DateTime(), existing_nullable=False,
        server_default=sa.text('CURRENT_TIMESTAMP'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'notificacion', 'fecha_creacion',
        existing_type=sa.DateTime(), existing_nullable=False,
        server_default=None,
    )
    op.alter_column(
        'verificacion', 'fecha_creacion',
        existing_type=sa.DateTime(), existing_nullable=False,
        server_default=None,
    )
    op.alter_column(
        'user', 'fecha_creacion',
        existing_type=sa.DateTime(), existing_nullable=False,
        server_default=None,
    )
