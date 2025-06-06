import os
from dotenv import load_dotenv, find_dotenv
from googletrans import Translator
import redis.asyncio as redis


load_dotenv(find_dotenv())

# Reuse a single Translator instance across calls
translator = Translator()

# Create a Redis connection pool
redis_pool = redis.ConnectionPool.from_url(
    os.environ["REDIS_URL"], encoding="utf-8", decode_responses=True
)

async def get_redis_client():
    """
    Returns a Redis client instance from a shared connection pool.

    This is a singleton function that returns the same Redis client instance every time it is called.
    """
    
    return redis.Redis(connection_pool=redis_pool)


async def detect(text: str) -> str:
    """
    Detects the language of the given text using googletrans and caches the result in Redis.

    Args:
        text (str): The text whose language needs to be detected.

    Returns:
        str: The detected language code (e.g., 'en' for English).
    """
    try:
        redis_client = await get_redis_client()
        key = f"lang:{text}"

        # Try to get from Redis
        cached_lang = await redis_client.get(key)
        if cached_lang:
            return cached_lang

        # Detect and cache
        detection_result = await translator.detect(text)
        detected_lang = detection_result.lang
        await redis_client.set(key, detected_lang, ex=3600)  # Cache for 1 hour
        return detected_lang

    except Exception as e:
        print(f"[Detect Error] {e}")
        return "en"  # Default to English on failure
    



async def translate_text(text: str, src: str = None):
    """Translate text from one language to another.

    Args:
        text (str): The text to translate.
        src (str): The source language to translate from.

    Returns:
        str: The translated text.
        tuple: The translated text and the target language if src is None.
    """
    if src:
        result = await translator.translate(text, dest=src)  
        return result.text
    else:
        result = await translator.translate(text)  
        return result.text, result.src
        
        

async def get_cached_language(question: str) -> str:
    """
    Checks if the language for a given question is cached in Redis, and if not, detects it and caches it.

    Args:
        question (str): The question whose language needs to be determined.

    Returns:
        str: The ISO 639-1 language code of the question (e.g., 'en' for English).
    """

    key = f"lang:{question}"
    
    redis_client = await get_redis_client()
    
    # Check if the language is already cached
    cached_lang = await redis_client.get(key)
    if cached_lang:
        return cached_lang
 
    # If not cached, detect the language and store it in Redis
    detected_lang = await detect(question)
    await redis_client.set(key, detected_lang, ex=3600)  # Cache for 1 hour
    return detected_lang
