from database import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, func


class Lead(Base):
    __tablename__ = "support_ticket"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thread_id = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(Text, nullable=False)
    phone = Column(Text, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)