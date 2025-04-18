from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv, find_dotenv
from routes.chat import chat_router

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

if __name__ == "__main__":
    load_dotenv(find_dotenv())
    uvicorn.run("main:app", port=8070)
