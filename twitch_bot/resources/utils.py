import json

from fastapi import Request
from pydantic import BaseModel


async def log_request_body(request: Request):
    body = await request.body()
    body_text = body.decode()
    body_dict = json.loads(body_text)
    print("Request body:", body_dict)  # Log the request body
    # Convert the body back to a format that can be used by the endpoint
    return body_dict


class SuccessResponseModel(BaseModel):
    success: bool


class ErrorResponseModel(BaseModel):
    error: str
    detail: str
