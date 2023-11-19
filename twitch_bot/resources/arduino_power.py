from enum import Enum
import os

from flask import jsonify, request
from flask.views import MethodView
from pydantic import BaseModel, validator

from twitch_bot.core.utils import load_environment
from twitch_bot.core.arduino import Arduino


class PowerCommand(Enum):
    ON = 'on'
    OFF = 'off'
    RESET = 'reset'


class ArduinoPut(BaseModel):
    power: PowerCommand


class ArduinoResource(MethodView):
    init_every_request = False

    def __init__(self):
        env = load_environment()
        for spotify_key in ('SPOTIPY_CLIENT_ID', 'SPOTIPY_CLIENT_SECRET'):
            os.environ[spotify_key] = env.get(spotify_key, None)
        self._ard = Arduino()

    def get(self):
        is_on = self._ard.is_on()
        return jsonify({'on': is_on})

    def put(self):
        try:
            command_data = ArduinoPut(**(request.json or {}))
        except Exception as err:
            return jsonify({'errors': [str(err)]}), 400

        if command_data.power == PowerCommand.ON:
            self._ard.on()
        elif command_data.power == PowerCommand.OFF:
            self._ard.off()
        elif command_data.power == PowerCommand.RESET:
            self._ard.reset()

        resp = jsonify({'success': True})
        print("resp:", resp)
        return resp
