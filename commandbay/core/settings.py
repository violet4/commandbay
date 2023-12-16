import os
from typing import Optional, List, Dict

from pydantic import BaseModel, Field
import yaml

from commandbay.utils.environ import environment as env


class Spotify(BaseModel):
    SPOTIPY_CLIENT_ID: str = ''
    SPOTIPY_CLIENT_SECRET: str = ''


class Twitch(BaseModel):
    bot_prefix: str = '!'
    # TMI_TOKEN: str = ''
    # CLIENT_ID: str = ''
    # CLIENT_SECRET: str = ''
    # BOT_NICK: str = ''
    # OWNER_ID: str = ''
    # re_greet_minutes: int = 60*4


class Settings(BaseModel):
    spotify: Spotify = Field(default_factory=lambda: Spotify(**{}))
    twitch: Twitch = Field(default_factory=lambda: Twitch(**{}))


class SettingsFile:
    filepath: str
    settings: Settings
    def __init__(self, filepath:str):
        self.settings = self.load(filepath) if os.path.exists(filepath) else Settings(**{})
        self.filepath = filepath

    def save(self):
        with open(self.filepath, 'w') as fw:
            yaml.safe_dump(self.settings.model_dump(), fw)

    def load(self, filepath:str):
        if os.path.exists(filepath):
            with open(filepath, 'r') as fr:
                data = yaml.safe_load(fr)
        else:
            data = dict()
        settings = Settings(**(data if data else {}))
        return settings


settings = SettingsFile(env.user_data_dir_path('settings.yaml'))
