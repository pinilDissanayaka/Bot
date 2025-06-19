from pydantic import BaseModel


class ChatRequest(BaseModel):
    web_name:str = "nolooptech"
    thread_id: str = "1"
    message: str = "Hello"
    

class ChatResponse(BaseModel):
    thread_id: str
    response: str
    
    