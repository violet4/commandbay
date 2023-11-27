import logging

from aiohttp import ClientSession
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from twitch_bot.resources.user import user_router
from twitch_bot.resources.app import app
from twitch_bot.resources.arduino_power import arduino_router
from twitch_bot.resources.kanboard import kanboard_router
from twitch_bot.resources.log_message import log_router
from twitch_bot.resources.random_num import random_router
from twitch_bot.resources.spotify import spotify_router, initialize_spotify
from twitch_bot.resources.do_tts import initialize_tts, tts_router


logging.basicConfig(level=logging.DEBUG)

initialize_spotify()
initialize_tts()

api_router = APIRouter()
api_router.include_router(prefix="/arduino",  router=arduino_router)
api_router.include_router(prefix="/kanboard", router=kanboard_router)
api_router.include_router(prefix='/spotify',  router=spotify_router)
api_router.include_router(prefix="/users", router=user_router)
api_router.include_router(prefix="/tts", router=tts_router)
api_router.include_router(prefix="/random/random", router=random_router)
api_router.include_router(prefix="/log", router=log_router)

@api_router.get("/")
async def hello_world():
    return 'this is a sample message from an http call'

app.include_router(prefix="/api", router=api_router)

@app.get('/{path:path}')
async def proxy_frontend(path: str):
    async with ClientSession() as sess:
        frontend_dev_server = 'http://localhost:3000'
        async with sess.get(f'{frontend_dev_server}/{path}') as resp:
            return HTMLResponse(
                await resp.text(),
                status_code=resp.status,
                media_type=resp.content_type,
            )
