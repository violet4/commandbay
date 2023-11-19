import logging

from twitch_bot.resources.app import app
from twitch_bot.resources.arduino_power import ArduinoResource
from twitch_bot.resources.kanboard import kanboard
from twitch_bot.resources.log_message import log_message
from twitch_bot.resources.random_num import random_num
from twitch_bot.resources.spotify import SpotifyResource
from twitch_bot.resources.do_tts import do_tts as tts


@app.route("/")
def hello_world():
    return 'this is a sample message from an http call'

app.add_url_rule('/spotify/song', view_func=SpotifyResource.as_view('spotify'))
app.add_url_rule('/arduino/power', view_func=ArduinoResource.as_view('arduino_power'))
app.route("/random/random")(random_num)
app.route("/log", methods=['POST'])(log_message)
app.route("/kanboard/new", methods=['POST'])(kanboard)
app.route("/tts", methods=['POST'])(tts)

logging.basicConfig(level=logging.DEBUG)
