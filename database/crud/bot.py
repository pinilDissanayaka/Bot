from database import Base, engine, SessionLocal
from database.models import ChatbotPrompt


def get(web_name: str):
    """
    Retrieve a ChatbotPrompt by web_name.
    
    Args:
        web_name (str): The name of the web for which to retrieve the prompt.
    
    Returns:
        ChatbotPrompt: The ChatbotPrompt object if found, otherwise None.
    """
    db = SessionLocal()
    try:
        prompt = db.query(ChatbotPrompt).filter(ChatbotPrompt.web_name == web_name).first()
        return prompt
    finally:
        db.close()  # Ensure the session is closed after use