import os
import logging

from twitch_bot.resources.app import app

from twitch_bot.resources.spotify import SpotifyResource
from twitch_bot.resources.arduino_power import ArduinoResource


@app.route("/")
def hello_world():
    return 'this is a sample message from an http call'

app.add_url_rule('/spotify/song', view_func=SpotifyResource.as_view('spotify'))
app.add_url_rule('/arduino/power', view_func=ArduinoResource.as_view('arduino_power'))

logging.basicConfig(level=logging.DEBUG)
