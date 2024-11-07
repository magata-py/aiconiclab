import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./orders.db")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Base model for SQLAlchemy ORM
Base = declarative_base()

# Session local dependency
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency function for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
