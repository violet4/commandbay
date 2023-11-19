import logging

from fastapi import Body

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
logging.basicConfig(level=logging.INFO)


def log_message(message:str=Body(...)):
    logger.info(message)
    return {'success': True}
