import os
from typing import TypeVar, Type
from abc import abstractmethod

from pydantic import BaseModel, Field, SecretStr as PydanticSecretStr
import yaml
from yaml.dumper import Dumper

from commandbay.utils.environ import environment as env


class SecretStr(PydanticSecretStr):
    def update(self, value:'SecretStr'):
        if value.get_secret_value() == str(self):
            return
        self._secret_value = value.get_secret_value()


T = TypeVar('T', bound='BaseModelUpdate')
class BaseModelUpdate(BaseModel):
    @abstractmethod
    def update(self: T, o: T) -> None:
        pass


class Spotify(BaseModel):
    SPOTIPY_CLIENT_ID: SecretStr = Field(
        default_factory=lambda: SecretStr(''), description="Spotify Client ID",
        examples=[""],
    )
    SPOTIPY_CLIENT_SECRET: SecretStr = Field(
        default_factory=lambda: SecretStr(''), description="Spotify Client Secret",
        examples=[""],
    )

    def update(self, o: 'Spotify'):
        self.SPOTIPY_CLIENT_ID.update(o.SPOTIPY_CLIENT_ID)
        self.SPOTIPY_CLIENT_SECRET.update(o.SPOTIPY_CLIENT_SECRET)


class Twitch(BaseModelUpdate):
    bot_prefix: str = '!'

    def update(self, o: 'Twitch'):
        self.bot_prefix = o.bot_prefix


class Settings(BaseModelUpdate):
    spotify: Spotify = Field(default_factory=lambda: Spotify(**{}))
    twitch: Twitch = Field(default_factory=lambda: Twitch(**{}))

    def update(self, o: 'Settings'):
        self.spotify.update(o.spotify)
        self.twitch.update(o.twitch)


class SettingsDumper(Dumper):
    """
    Enable the ability to save SecretStr secret value when writing to file
    """
    def represent_SecretStr(self, data: SecretStr):
        return self.represent_scalar('tag:yaml.org,2002:str', data.get_secret_value())

SettingsDumper.add_representer(SecretStr, SettingsDumper.represent_SecretStr)


class SettingsFile:
    filepath: str
    settings: Settings
    def __init__(self, filepath:str):
        self.settings = self.load(filepath) if os.path.exists(filepath) else Settings(**{})
        self.filepath = filepath

    def save(self):
        with open(self.filepath, 'w') as fw:
            yaml.dump(self.settings.model_dump(), fw, Dumper=SettingsDumper)

    def load(self, filepath:str):
        if os.path.exists(filepath):
            with open(filepath, 'r') as fr:
                data = yaml.safe_load(fr)
        else:
            data = dict()
        settings = Settings(**(data if data else {}))
        return settings

    def update(self, s: Settings):
        self.settings.update(s)


settings = SettingsFile(env.user_data_dir_path('settings.yaml'))
