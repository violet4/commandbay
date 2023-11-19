from enum import Enum
import os

from fastapi import APIRouter, Body

from twitch_bot.core.utils import load_environment
from twitch_bot.core.spotify import Spotify


class SpotifyMethod(Enum):
    ADD = 'add'


class SpotifyResource:
    router = APIRouter()
    init_every_request = False

    def __init__(self):
        env = load_environment()
        for spotify_key in ('SPOTIPY_CLIENT_ID', 'SPOTIPY_CLIENT_SECRET'):
            os.environ[spotify_key] = env.get(spotify_key, None)
        self._spotify = Spotify()

    @router.get('/song')
    async def get_current_song(self):
        song_str = self._spotify.get_current_song_str()
        return {'current_song': song_str}

    @router.put('/song')
    async def put(self, method:SpotifyMethod=Body(...)):
        if method == 'add':
            error_dict = self._spotify.add()
            if error_dict is None:
                return {'success': True}
            else:
                return {'errors': [error_dict]}
