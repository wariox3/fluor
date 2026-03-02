from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from decouple import config

DB_HOST = config("DB_MASTER_HOST")
DB_USER = config("DB_MASTER_USER")
DB_PASSWORD = config("DB_MASTER_PASSWORD")
DB_NAME = config("DB_MASTER_NAME")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600
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