import os
from fastapi import APIRouter, HTTPException, Depends
from schema import ChatRequest, ChatResponse
from agent import get_chat_response, build_graph
from functools import lru_cache
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from redis.asyncio import Redis


chat_router = APIRouter(
    prefix="/chat", 
    tags=["Chat-bot"]
)


# Initialize rate limiter
@chat_router.on_event("startup")
async def startup_event():
    """
    Initialize the FastAPILimiter extension during the startup event of the chat_router.

    This function is called during the startup event of the chat_router, and is responsible
    for initializing the FastAPILimiter extension. The extension is initialized by creating
    a Redis client from the REDIS_URL environment variable, and then calling the init method
    of the FastAPILimiter class with the Redis client as an argument.
    """
    redis_client = Redis.from_url(os.environ["REDIS_URL"])
    await FastAPILimiter.init(redis_client)


@lru_cache(maxsize=None)
def get_cached_graph():
    """Returns the cached chatbot state machine graph.
    
    The graph is built using the `build_graph` function and cached using the `lru_cache` decorator.
    This means that the graph is only built once and the same instance is returned every time this function is called.
    """
    
    return build_graph()


@chat_router.post("/", response_model=ChatResponse, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def chat(request: ChatRequest):
    """
    Responds to a user's question using the chatbot state machine
    """
    try:
        graph = get_cached_graph()
        
        return ChatResponse(
            response=await get_chat_response(graph=graph, question=request.message, thread_id=request.thread_id)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")