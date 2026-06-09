from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

DATABASE_URL = "postgresql://postgres:1234@localhost/bookify_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker (
    autoflush=False,
    autocommit=False,
    bind=engine
)

Base = declarative_base()
