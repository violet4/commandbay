import os
import random
from html import unescape

from flask import Flask, request

from twitch_bot.spotify import Spotify
from twitch_bot.kanboard_integ import Kanboard
from twitch_bot.utils import load_environment
from twitch_bot.tts import tts
from twitch_bot.arduino import Arduino


app = Flask(__name__)

@app.route("/")
def hello_world():
    return 'this is a sample message from an http call'

env = load_environment()
for spotify_key in ('SPOTIPY_CLIENT_ID', 'SPOTIPY_CLIENT_SECRET'):
    os.environ[spotify_key] = env.get(spotify_key, None)


spotify = Spotify()

@app.route("/spotify/song")
def song():
    if spotify is None:
        return ''
    song_str = spotify.get_current_song_str()
    print("SONG STRING", song_str)
    return song_str if song_str else "Failed to get info from Spotify API"


kb = Kanboard()

@app.route("/kanboard/new", methods=['POST'])
def remind():
    if kb is None:
        return 'kanboard connection is not established', 503
    if request.method != 'POST':
        return 'only POST method supported', 405

    if request.json is None:
        return 'no request data provided', 400

    print(request.json)
    remind_title = request.json.get('title', None)
    if remind_title is None:
        return "reminder title must be provided in the 'title' value of your json data", 400
    if not isinstance(remind_title, str):
        return 'unexpected title type; expected str, got %s' % type(remind_title), 422

    title_prefix = '!remind '
    if remind_title.startswith(title_prefix):
        remind_title = remind_title[len(title_prefix):]

    kb.add_task(remind_title)
    return 'success', 200


@app.route("/random/random")
def random_num():
    max_val = request.args.get('max', None)
    if max_val is None:
        return 'max is required', 400
    try:
        max_val = int(max_val)
    except:
        return 'max must be an integer value', 422
    return str(random.randint(1, max_val)), 200


@app.route("/tts", methods=['POST'])
def do_tts():
    if (not tts) or tts.tts_disabled:
        return 'tts is not enabled', 503
    if request.method != 'POST':
        return 'only POST method supported', 405

    if request.json is None:
        return 'no request data provided', 400

    print(request.json)
    username = request.json.get('user', None)
    message = request.json.get('message', None)
    for key, value in (('username', username), ('message', message)):
        if value is None:
            return f"tts command provided no {key}", 400
        if not isinstance(message, str):
            return f'unexpected {key} type; expected str, got %s' % type(value), 422

    message = unescape(message)

    tts.say(username)
    tts.say('says')
    tts.say(message)
    tts.runAndWait()

    return 'success', 200


arduino = Arduino()
@app.route("/arduino/power", methods=['PUT'])
def arduino_power():
    if request.method != 'PUT':
        return 'only PUT method supported', 405

    if request.json is None:
        return 'no request data provided', 400

    power = request.json.get('power', None)
    if power is None:
        return "provide `power` in your json body", 400

    if power not in ('on', 'off', 'reset'):
        return "value of `power` must be either `on` or `off`", 422

    if power == 'on':
        arduino.on()
    elif power == 'off':
        arduino.off()
    elif power == 'reset':
        arduino.reset()

    return 'success', 200
