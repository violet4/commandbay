from html import unescape
import json

from fastapi import Request
from pydantic import BaseModel


async def log_request_body(request: Request):
    body = await request.body()
    body_text = body.decode()
    body_dict = json.loads(body_text)
    return body_dict


class SuccessResponseModel(BaseModel):
    success: bool


class ErrorResponseModel(BaseModel):
    error: str
    detail: str


class HtmlBaseModel(BaseModel):
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            if isinstance(v, str):
                kwargs[k] = unescape(v)
        super().__init__(*args, **kwargs)
