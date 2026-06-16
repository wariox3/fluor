from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, declarative_base
from decouple import config
from app.core.config import DB_TIME_ZONE


@event.listens_for(Engine, "connect")
def _set_db_timezone(dbapi_connection, connection_record):
    """Fija la zona horaria en cada conexión MySQL (master y tenants).

    Al escuchar sobre la clase base Engine, aplica a todos los engines del
    proyecto, así NOW()/CURRENT_TIMESTAMP y los server_default quedan en hora local.
    """
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SET time_zone = %s", (DB_TIME_ZONE,))
    finally:
        cursor.close()

DB_HOST = config("DB_MASTER_HOST")
DB_PORT = config("DB_MASTER_PORT", default="3306")
DB_USER = config("DB_MASTER_USER")
DB_PASSWORD = config("DB_MASTER_PASSWORD")
DB_NAME = config("DB_MASTER_NAME")

DB_POOL_SIZE = config("DB_MASTER_POOL_SIZE", default="10", cast=int)
DB_MAX_OVERFLOW = config("DB_MASTER_MAX_OVERFLOW", default="20", cast=int)
DB_POOL_TIMEOUT = config("DB_MASTER_POOL_TIMEOUT", default="30", cast=int)

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,  # < wait_timeout del servidor (3600s) para no usar conexiones ya cerradas
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_timeout=DB_POOL_TIMEOUT,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_master_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()