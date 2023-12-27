import time

from fastapi import APIRouter, Query


test_router = APIRouter()

@test_router.get("/sleep")
async def sleep_time(seconds:float=Query(...)):
    time.sleep(seconds)
    return {}
