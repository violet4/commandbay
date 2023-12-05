import random

from fastapi import APIRouter, HTTPException, Query


random_router = APIRouter()

@random_router.get("/random/random")
async def random_num(max_val: int = Query(..., alias='max')):
    if max_val <= 1:
        raise HTTPException(status_code=422, detail="max must be a positive integer")
    return random.randint(1, max_val)
