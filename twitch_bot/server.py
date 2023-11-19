import logging

from twitch_bot.resources.app import app
from twitch_bot.resources.arduino_power import arduino_router
from twitch_bot.resources.kanboard import KanboardResource
from twitch_bot.resources.log_message import log_message
from twitch_bot.resources.random_num import random_num
from twitch_bot.resources.spotify import SpotifyResource
from twitch_bot.resources.do_tts import do_tts as tts, initialize_tts


logging.basicConfig(level=logging.DEBUG)

initialize_tts()

@app.get("/")
async def hello_world():
    return 'this is a sample message from an http call'

kanboard_resource = KanboardResource()
spotify_resource = SpotifyResource()

app.include_router(prefix="/arduino",  router=arduino_router)
app.include_router(prefix="/kanboard", router=kanboard_resource.router)
app.include_router(prefix='/spotify',  router=spotify_resource.router)

app.get("/random/random")(random_num)
app.post("/log")(log_message)
app.post("/tts")(tts)
