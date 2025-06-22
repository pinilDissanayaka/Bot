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
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()