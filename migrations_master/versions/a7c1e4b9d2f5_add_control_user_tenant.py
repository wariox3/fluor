"""add control a user_tenant

Revision ID: a7c1e4b9d2f5
Revises: f2b8d5a7e1c6
Create Date: 2026-10-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7c1e4b9d2f5'
down_revision: Union[str, Sequence[str], None] = 'f2b8d5a7e1c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('user_tenant', sa.Column('control', sa.Boolean(), server_default=sa.false(), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('user_tenant', 'control')
