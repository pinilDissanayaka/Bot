from pydantic import BaseModel


class ChatRequest(BaseModel):
    thread_id: str = "1"
    message: str = "Hello"
    

class ChatResponse(BaseModel):
    response: str
    
    