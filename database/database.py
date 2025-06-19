import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

Base = declarative_base()

engine = create_engine(os.getenv("DATABASE_URL"), echo=True, future=True)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
