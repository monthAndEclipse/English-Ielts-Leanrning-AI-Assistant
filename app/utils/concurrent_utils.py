from contextlib import asynccontextmanager
import asyncio
from fastapi import HTTPException

@asynccontextmanager
async def try_acquire(semaphore):
    try:
        #wait until you get the semaphore,not recommended in this case
        #await semaphore.acquire()
        #wait for 5 second,since translation task is always lengthy
        await asyncio.wait_for(semaphore.acquire(), timeout=5)
        try:
            yield
        finally:
            semaphore.release()
    except asyncio.TimeoutError:
        raise HTTPException(status_code=503, detail="Too many concurrent tasks")