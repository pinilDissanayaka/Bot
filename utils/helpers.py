import asyncio
import concurrent.futures

def run_sync(fn, *args, **kwargs):
    """
    Run a sync function in a thread pool, and return a coroutine.
    
    Use this to call a function that is not async, but is blocking, and
    you don't want to block the event loop.
    
    """
    
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        return loop.run_in_executor(pool, lambda: fn(*args, **kwargs))