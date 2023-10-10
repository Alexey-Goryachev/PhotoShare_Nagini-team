from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#connect to DB postgreSQL
# POSTGRES_DB=photoshare
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=123456
# POSTGRES_PORT=5432
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:123456@localhost:5432/photoshare"


engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
