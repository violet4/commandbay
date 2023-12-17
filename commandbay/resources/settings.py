import logging

from fastapi import APIRouter, Body

from commandbay.core.settings import Settings, settings

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
logging.basicConfig(level=logging.INFO)

settings_router = APIRouter()


@settings_router.get("/openapi.json")
def get_settings_schema():
    return Settings.model_json_schema()


@settings_router.get("", response_model=Settings)
def get_settings():
    return Settings.model_dump(settings.settings)


@settings_router.put("")
def put_settings(settings_data:Settings=Body(...)):
    settings.update(settings_data)  #TODO:update the data with audit trail instead of just overwriting variable
    settings.save()
    return settings.settings.model_dump()
