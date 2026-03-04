from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decouple import config
from fastapi import Depends, HTTPException, status
from app.core.security import get_current_user
from sqlalchemy.orm import declarative_base

Base = declarative_base()

DB_HOST = config("DB_HOST")
DB_PORT = config("DB_PORT", default="3306")
DB_USER = config("DB_USER")
DB_PASSWORD = config("DB_PASSWORD")


def get_tenant_engine(database_name: str):
    DATABASE_URL = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{database_name}"
    )

    return create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600
    )


def get_tenant_db(current_user=Depends(get_current_user)):
    database_name = current_user.get("empresa_id")

    if not database_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no tiene empresa asignada"
        )

    engine = get_tenant_engine(database_name)
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()