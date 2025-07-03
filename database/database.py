import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from dotenv import load_dotenv, find_dotenv
from typing import Generator


load_dotenv(find_dotenv())

Base = declarative_base()

engine = create_engine(os.getenv("DATABASE_URL"), echo=True, future=True)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    """
    A generator that yields a database session object.

    The database session is opened when the generator is called and
    closed when the generator is exited. This function is meant to
    be used as a FastAPI dependency.

    Yields:
        Session: A database session object.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()