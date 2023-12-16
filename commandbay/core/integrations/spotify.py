import time
import logging
from typing import Optional

from spotipy.client import Spotify as Spotipy
from spotipy.oauth2 import SpotifyOAuth

from commandbay.core.utils import log_formatter

logger = logging.getLogger(__name__)


class Spotify(Spotipy):
    next_song_info_time: float
    current_song_info: str
    def __init__(self):
        super().__init__(oauth_manager=SpotifyOAuth(
            redirect_uri='http://localhost:9180',
            scope=[
                'user-read-currently-playing',
                'user-read-playback-state',
            ],
        ))
        self.next_song_info_time = 0.0
        self.current_song_info = ''

    def _get_current_playback(self, retry_count=5) -> dict:
        for _ in range(retry_count):
            try:
                pb = self.current_playback()
                if isinstance(pb, dict):
                    return pb
                else:
                    logger.error("current playback info from spotify API didn't return dict, instead returned: %s", pb)
            except Exception as e:
                logger.exception("failed to get current playback info from spotify API")
                time.sleep(1.235)
        msg = "failed to get current playback info from spotify API %s times" % (retry_count,)
        logger.error(msg)
        return {'error':msg}

    def get_current_song_str(self, force_response:bool=False) -> str:
        """
        implement force_response
        needed test cases:
        * no song playing (and hasn't in a while so the api call will not return a current song)
        """
        if self.next_song_info_time > 0 and time.time() < self.next_song_info_time:
            remaining = self.next_song_info_time - time.time()
            return f"{self.current_song_info} - Ends in {remaining//60:.0f}:{remaining%60//1:>02.0f}"

        pb = self._get_current_playback()
        if 'error' in pb:
            return ''

        duration_ms = pb['item']['duration_ms']
        progress_ms = pb['progress_ms']
        remaining_ms = duration_ms - progress_ms
        remaining_seconds = remaining_ms / 1000
        self.next_song_info_time = time.time() + remaining_seconds

        song_name = pb['item']['name']
        artists_str = ', '.join(a['name'] for a in pb['item']['artists'])
        full_str = f'{song_name} - {artists_str}'
        self.current_song_info = full_str
        remaining = remaining_seconds
        return f"{self.current_song_info} - Ends in {remaining//60:.0f}:{remaining%60//1:>02.0f}"

    def add(self) -> Optional[dict]:
        """
        :retval: None if success, error dict otherwise
        """
        pb = self._get_current_playback()
        if pb is None:
            return {'message': 'failed to get current playback info from spotify'}
        return None



__all__ = (
    'Spotify',
)

# if __name__ == '__main__':
#     if logger.handlers:
#         logger.handlers[0].setFormatter(log_formatter)
#     logging.getLogger().handlers[0].setFormatter(log_formatter)

