from enum import Enum
from errno import ERESTART
from typing import Union

from fastapi import APIRouter, Body
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

from twitch_bot.core.arduino import Arduino


_arduino = Arduino()
arduino_router = APIRouter()


class PowerCommandEnum(str, Enum):
    on = 'on'
    off = 'off'
    reset = 'reset'


class PowerCommandModel(BaseModel):
    power: PowerCommandEnum


class PowerStatusModel(BaseModel):
    on: bool


class ArduinoError(BaseModel):
    message: str


class ErrorResponseModel(BaseModel):
    error: str
    detail: str

class SuccessResponseModel(BaseModel):
    success: bool


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
