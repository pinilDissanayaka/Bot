from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv, find_dotenv
from database import Base, engine
from routes.chat import chat_router
from database.models import ChatbotPrompt

app = FastAPI()


app.include_router(chat_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def health_check():
    return {"status": "Server running"}

@app.on_event("startup")
def on_startup():
    load_dotenv(find_dotenv())
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    load_dotenv(find_dotenv())
    uvicorn.run("main:app", port=8070)
