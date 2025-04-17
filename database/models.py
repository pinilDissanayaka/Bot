from sqlalchemy import create_engine, Column, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from database.database import Base
from datetime import datetime

from utils import vector_store


class Bot(Base):
    __tablename__ = "bot"
    
    id = Column(Integer, primary_key=True, index=True)
    web_name=Column(Text)
    base_url = Column(Text)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())
    



    
    
    

    
    


    
    
    

    

