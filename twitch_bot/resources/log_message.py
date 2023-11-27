from enum import StrEnum, auto
import logging
from typing import Optional

from fastapi import APIRouter, Body
from pydantic import BaseModel

from twitch_bot.resources.utils import SuccessResponseModel

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
logging.basicConfig(level=logging.INFO)

log_router = APIRouter()


class LogLevelName(StrEnum):
    CRITICAL = auto()
    FATAL = auto()
    ERROR = auto()
    WARNING = auto()
    WARN = auto()
    INFO = auto()
    DEBUG = auto()
    NOTSET = auto()


class LogMessageSchema(BaseModel):
    level: LogLevelName = LogLevelName.INFO
    message: str


@log_router.post("")
def log_message(message:LogMessageSchema=Body(...)):
    method = getattr(logger, message.level)
    method(message.message)
    return SuccessResponseModel(success=True)
