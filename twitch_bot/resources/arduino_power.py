from enum import Enum
from errno import ERESTART
import json
import os
from types import NoneType
from typing import Optional, Union

from fastapi import APIRouter, Body, Request
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

from twitch_bot.core.arduino import Arduino


class PowerCommandEnum(str, Enum):
    on = 'on'
    off = 'off'
    reset = 'reset'


class PowerCommandModel(BaseModel):
    power: PowerCommandEnum


class PowerStatusModel(BaseModel):
    on: bool


async def log_request_body(request: Request):
    body = await request.body()
    body_text = body.decode()
    body_dict = json.loads(body_text)
    print("Request body:", body_dict)  # Log the request body
    # Convert the body back to a format that can be used by the endpoint
    return body_dict

class ArduinoError(BaseModel):
    message: str


class ErrorResponseModel(BaseModel):
    error: str
    detail: str

class SuccessResponseModel(BaseModel):
    success: bool

_arduino = Arduino()
arduino_router = APIRouter()

@arduino_router.get(
    '/power',
    response_model=Union[PowerStatusModel, ErrorResponseModel],
    responses={503: {"model": ErrorResponseModel}}
)
async def get():
    try:
        is_on = _arduino.is_on()
    except Exception as e:
        error_response = ErrorResponseModel(error="couldn't communicate with arduino", detail=str(e))
        raise HTTPException(503, detail=error_response.model_dump())

    return PowerStatusModel(on=is_on)

@arduino_router.put(
    '/power',
    response_model=Union[SuccessResponseModel, ErrorResponseModel],
    responses={503: {"model": ErrorResponseModel}}
)
async def update_arduino_power(command:PowerCommandModel=Body(...)):
    try:
        if command.power == PowerCommandEnum.on:
            _arduino.on()
        elif command.power == PowerCommandEnum.off:
            _arduino.off()
        elif command.power == PowerCommandEnum.reset:
            _arduino.reset()
    except Exception as e:
        error = ErrorResponseModel(error="couldn't send command to the arduino", detail=str(e))
        raise HTTPException(503, detail=error.model_dump())

    return SuccessResponseModel(success=True)
