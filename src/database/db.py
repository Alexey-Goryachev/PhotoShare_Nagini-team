from sqlalchemy import create_engine, Column, String, Integer, func
from sqlalchemy.orm import sessionmaker
from typing import List
from sqlalchemy.sql.sqltypes import DateTime
from src.conf.config import settings

#connect to DB postgreSQL
# POSTGRES_DB=postgres
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=123456
# POSTGRES_PORT=5432
SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url


engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
