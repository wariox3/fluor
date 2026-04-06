import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Agrega la raíz del proyecto al path para poder importar app.*
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa el engine y Base del master DB
from app.core.master_database import DATABASE_URL, Base

# Importa todos los modelos del master para que Alembic los detecte
from app.modules.auth.models.tenant import Tenant
from app.modules.auth.models.user import User
from app.modules.auth.models.api_key import ApiKey
from app.modules.auth.models.notificacion import Notificacion
from app.modules.mas.models.credito_solicitud import CreditoSolicitud

# Alembic Config
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Apunta a los metadatos del master DB
target_metadata = Base.metadata

# Inyecta la URL desde las variables de entorno (ignora la del .ini)
config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
