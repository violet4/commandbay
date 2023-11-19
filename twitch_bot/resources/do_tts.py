from html import unescape

from flask import request

from twitch_bot.core.tts import tts
from twitch_bot.resources.app import app


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
        if not isinstance(value, str):
            return f'unexpected {key} type; expected str, got %s' % type(value), 422

    message = unescape(message)

    tts.say(username)
    tts.say('says')
    tts.say(message)
    tts.runAndWait()

    return 'success', 200