from enum import Enum
import os
from typing import Optional

from fastapi import APIRouter, Body

from commandbay.core.utils import load_environment
from commandbay.core.spotify import Spotify


class SpotifyMethod(Enum):
    ADD = 'add'


spotify_router = APIRouter()
_spotify: Optional[Spotify] = None


def initialize_spotify():
    global _spotify
    env = load_environment()
    for spotify_key in ('SPOTIPY_CLIENT_ID', 'SPOTIPY_CLIENT_SECRET'):
        os.environ[spotify_key] = env.get(spotify_key, None)
    _spotify = Spotify()


def verify_initialized():
    if _spotify is None:
        raise Exception("spotify not initialized; must call initialize_spotify()")
    return _spotify


@spotify_router.get('/song')
async def get_current_song():
    _spotify = verify_initialized()
    song_str = _spotify.get_current_song_str()
    return {'current_song': song_str}


@spotify_router.put('/song')
async def put(method:SpotifyMethod=Body(...)):
    _spotify = verify_initialized()
    if method == 'add':
        error_dict = _spotify.add()
        if error_dict is None:
            return {'success': True}
        else:
            return {'errors': [error_dict]}
