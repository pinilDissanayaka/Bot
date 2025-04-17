from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os   
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

# Create the base class for all models
Base = declarative_base()


# Create an engine and bind it to the base
engine = create_engine(os.getenv("DATABASE_URL"), echo=True)

# Create the tables in the database

# Create a session
Session = sessionmaker(bind=engine)

session = Session()
