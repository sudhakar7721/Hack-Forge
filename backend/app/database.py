import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Load backend/.env when running from the backend directory.
load_dotenv()

# MySQL is the default database for this project.
# Replace the example password in backend/.env with your own MySQL password.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:change_me@127.0.0.1:3306/maatram_db?charset=utf8mb4",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
