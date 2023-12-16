from enum import Enum
import os
from typing import Optional

from fastapi import APIRouter, Body, HTTPException

from commandbay.core.settings import settings
from commandbay.core.integrations.spotify import Spotify


class SpotifyMethod(Enum):
    ADD = 'add'


spotify_router = APIRouter()
_spotify: Optional[Spotify] = None


def initialize_spotify():
    global _spotify
    a = os.environ['SPOTIPY_CLIENT_ID'] = settings.settings.spotify.SPOTIPY_CLIENT_ID or ''
    b = os.environ['SPOTIPY_CLIENT_SECRET'] = settings.settings.spotify.SPOTIPY_CLIENT_SECRET or ''
    if a and b:
        _spotify = Spotify()


def verify_initialized():
    global _spotify
    if _spotify is None:
        raise Exception("spotify not initialized; must call initialize_spotify()")
    return _spotify


@spotify_router.get('/song')
async def get_current_song():
    _spotify = verify_initialized()
    if _spotify is None:
        raise HTTPException(503, detail="Not connected to spotify")
    song_str = _spotify.get_current_song_str()
    return {'current_song': song_str}


@spotify_router.put('/song')
async def put(method:SpotifyMethod=Body(...)):
    _spotify = verify_initialized()
    if method == SpotifyMethod.ADD.value:
        error_dict = _spotify.add()
        if error_dict is None:
            return {'success': True}
        else:
            return {'errors': [error_dict]}
