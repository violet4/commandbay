import os

from flask import jsonify, request
from flask.views import MethodView
from pydantic import BaseModel, validator

from twitch_bot.core.utils import load_environment
from twitch_bot.core.spotify import Spotify


class SpotifyAdd(BaseModel):
    method: str

    @validator('method')
    def method_must_be_add(cls, v):
        if v != 'add':
            raise ValueError('method must be "add"')
        return v


class SpotifyResource(MethodView):
    init_every_request = False

    def __init__(self):
        env = load_environment()
        for spotify_key in ('SPOTIPY_CLIENT_ID', 'SPOTIPY_CLIENT_SECRET'):
            os.environ[spotify_key] = env.get(spotify_key, None)
        self._spotify = Spotify()

    def get(self):
        song_str = self._spotify.get_current_song_str()
        return jsonify({'current_song': song_str})

    def put(self):
        try:
            spotify_method_data = SpotifyAdd(**(request.json or {}))
        except Exception as err:
            return jsonify({'errors': [str(err)]}), 400

        if spotify_method_data.method == 'add':
            error = self._spotify.add()
            if error is None:
                return 'success!', 200
            else:
                return str(error), 200
