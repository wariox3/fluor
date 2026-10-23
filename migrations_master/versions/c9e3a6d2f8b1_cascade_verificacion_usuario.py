"""cascade delete verificacion al eliminar usuario

Revision ID: c9e3a6d2f8b1
Revises: b5d8e1a4c7f2
Create Date: 2026-10-22 00:00:00.000000

Reemplaza la llave foránea verificacion.usuario_id por una con ON DELETE CASCADE,
para que al borrar un usuario (incluso con un DELETE manual) se borren sus
verificaciones. El nombre de la llave actual lo generó MySQL y puede variar
entre entornos, por eso se consulta antes de eliminarla.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9e3a6d2f8b1'
down_revision: Union[str, Sequence[str], None] = 'b5d8e1a4c7f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

FK_NOMBRE = 'fk_verificacion_usuario_id'


def _fk_actual() -> str | None:
    return op.get_bind().execute(sa.text("""
        SELECT CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'verificacion'
          AND COLUMN_NAME = 'usuario_id'
          AND REFERENCED_TABLE_NAME = 'user'
    """)).scalar()


def upgrade() -> None:
    """Upgrade schema."""
    actual = _fk_actual()
    if actual:
        op.drop_constraint(actual, 'verificacion', type_='foreignkey')
    op.create_foreign_key(FK_NOMBRE, 'verificacion', 'user', ['usuario_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(FK_NOMBRE, 'verificacion', type_='foreignkey')
    op.create_foreign_key(FK_NOMBRE, 'verificacion', 'user', ['usuario_id'], ['id'])
