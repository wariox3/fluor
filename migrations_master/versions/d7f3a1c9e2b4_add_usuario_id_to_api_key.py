"""add usuario_id to api_key

Revision ID: d7f3a1c9e2b4
Revises: 2c50afaba5dc
Create Date: 2026-09-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7f3a1c9e2b4'
down_revision: Union[str, Sequence[str], None] = '2c50afaba5dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Nullable: las API keys existentes no tienen usuario asociado.
    op.add_column('api_key', sa.Column('usuario_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_api_key_usuario_id', 'api_key', 'user', ['usuario_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_api_key_usuario_id', 'api_key', type_='foreignkey')
    op.drop_column('api_key', 'usuario_id')
