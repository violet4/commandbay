from html import unescape

from fastapi import Body

from twitch_bot.core.tts import tts
from twitch_bot.resources.app import app


def do_tts(username:str=Body(...), message:str=Body(...)):
    message = unescape(message)

    tts.say(username)
    tts.say('says')
    tts.say(message)
    tts.runAndWait()

    return {'success': True}
