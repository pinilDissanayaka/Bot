from database import Base, engine, SessionLocal
from database.models import ChatbotPrompt


def get(web_name: str, db):
    try:
        data = db.query(ChatbotPrompt).filter(ChatbotPrompt.web_name == web_name).first()
        return data
    finally:
        db.close()  