import os
import re
import tempfile
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from schema import ChatRequest, ChatResponse
from agent import get_chat_response, build_graph
from functools import lru_cache
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from redis.asyncio import Redis
from sqlalchemy.orm import Session
from database import get_db
from database.crud import get
from utils import logger
from utils import Loader, VectorStore



vector_store_router = APIRouter(
    prefix="/vector_store", 
    tags=["Vector Store"]
)


@vector_store_router.on_event("startup")
async def startup_event():  
    """
    Initialize the FastAPILimiter extension during the startup event of the vector_store_router.

    This function is called during the startup event of the vector_store_router, and is responsible
    for initializing the FastAPILimiter extension. The extension is initialized by creating
    a Redis client from the REDIS_URL environment variable, and then calling the init method
    of the FastAPILimiter class with the Redis client as an argument.
    """
    logger.info("Vector Store router startup event triggered.")
    redis_client = Redis.from_url(os.environ["REDIS_URL"])
    await FastAPILimiter.init(redis_client)
    


@vector_store_router.post("/create")
async def create_vector_store(
    files: list[UploadFile] = File(None)
):
    with tempfile.TemporaryDirectory(dir=os.getcwd()) as temp_dir:
        uploaded_file_paths = []
        
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            uploaded_file_paths.append(file_path)
        
        loader = Loader(
            file_paths=uploaded_file_paths,
        )
        
        loaded_content = await loader.load()
        
    vectore_store= VectorStore(web_name="noopy")
    
    new_vector_store = vectore_store.create_vector_store(text=loaded_content)
    
    return {"message": "Vector store created successfully", "vector_store": new_vector_store}
