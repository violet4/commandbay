import logging

from aiohttp import ClientSession
from fastapi.responses import HTMLResponse

from twitch_bot.resources.app import app
from twitch_bot.resources.arduino_power import arduino_router
from twitch_bot.resources.kanboard import kanboard_router
from twitch_bot.resources.log_message import log_message
from twitch_bot.resources.random_num import random_num
from twitch_bot.resources.spotify import spotify_router, initialize_spotify
from twitch_bot.resources.do_tts import post_tts_message, post_tts_message, initialize_tts


logging.basicConfig(level=logging.DEBUG)

initialize_spotify()
initialize_tts()


@app.get("/")
async def hello_world():
    return 'this is a sample message from an http call'


app.include_router(prefix="/arduino",  router=arduino_router)
app.include_router(prefix="/kanboard", router=kanboard_router)
app.include_router(prefix='/spotify',  router=spotify_router)

app.get("/random/random")(random_num)
app.post("/log")(log_message)
app.post("/tts")(post_tts_message)

@app.get('/{path:path}')
async def proxy_frontend(path: str):
    async with ClientSession() as sess:
        elm_dev_server = 'http://localhost:8000'
        async with sess.get(f'{elm_dev_server}/{path}') as resp:
            return HTMLResponse(await resp.text(), status_code=resp.status)
