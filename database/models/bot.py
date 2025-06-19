from database import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, func


class ChatbotPrompt(Base):
    __tablename__ = "chatbot"

    id = Column(Integer, primary_key=True, autoincrement=True)
    web_name = Column(String(255), nullable=False, index=True)
    vector_store_path = Column(Text, nullable=False)
    agent_prompt = Column(Text, nullable=False)
    generate_prompt = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
