"""cascade delete notificacion al eliminar usuario

Revision ID: d4f7b2e9a5c3
Revises: c9e3a6d2f8b1
Create Date: 2026-10-22 00:00:00.000000

Reemplaza la llave foránea notificacion.usuario_id por una con ON DELETE CASCADE,
para que al borrar un usuario (incluso con un DELETE manual) se borren sus
notificaciones. El nombre de la llave actual lo generó MySQL y puede variar
entre entornos, por eso se consulta antes de eliminarla.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4f7b2e9a5c3'
down_revision: Union[str, Sequence[str], None] = 'c9e3a6d2f8b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

FK_NOMBRE = 'fk_notificacion_usuario_id'


def _fk_actual() -> str | None:
    return op.get_bind().execute(sa.text("""
        SELECT CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'notificacion'
          AND COLUMN_NAME = 'usuario_id'
          AND REFERENCED_TABLE_NAME = 'user'
    """)).scalar()


def upgrade() -> None:
    """Upgrade schema."""
    actual = _fk_actual()
    if actual:
        op.drop_constraint(actual, 'notificacion', type_='foreignkey')
    op.create_foreign_key(FK_NOMBRE, 'notificacion', 'user', ['usuario_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(FK_NOMBRE, 'notificacion', type_='foreignkey')
    op.create_foreign_key(FK_NOMBRE, 'notificacion', 'user', ['usuario_id'], ['id'])
