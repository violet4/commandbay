import sys
import os
from os.path import dirname
import platform as sys_platform
import pathlib

from pydantic import BaseModel, Field


base_app_data_dir_path = dirname(dirname(dirname(os.path.abspath(__file__))))
def app_data_dir_path(*relative_path):
    return os.path.join(base_app_data_dir_path, *relative_path)


base_user_data_dir_path = os.path.abspath(getattr(sys, '_MEIPASS', base_app_data_dir_path))
def user_data_dir_path(*relative_path):
    return os.path.join(base_user_data_dir_path, *relative_path)


class Platform(BaseModel):
    data_dir: str
    platform_name: str = sys_platform.system()

    @classmethod
    def get_platform(cls) -> 'Platform':
        os_name: str = sys_platform.system()

        # Determine base directory
        if os_name == 'Windows':
            plat = Windows
        elif os_name == 'Darwin':  # macOS
            plat = MacOS
        else:  # Linux and other Unix-like OS
            plat = Linux
        platform_obj = plat()
        pathlib.Path(platform_obj.data_dir).mkdir(parents=True, exist_ok=True)
        return platform_obj


class Windows(Platform):
    data_dir: str = Field(default_factory=lambda: os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'commandbay'))


class MacOS(Platform):
    data_dir: str = Field(default_factory=lambda: os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'commandbay'))


class Linux(Platform):
    data_dir: str = Field(default_factory=lambda: os.path.join(os.path.expanduser('~'), '.local', 'share', 'commandbay'))


class Backend(BaseModel):
    static_backend_files_path: str = Field(default_factory=lambda:
        os.environ.get(
            'STATIC_BACKEND_FILES_PATH',
            app_data_dir_path('static'),
            # 'frontend/out',
        )
    )


class Frontend(BaseModel):
    static_frontend: bool = False
    frontend_port: str = Field(default_factory=lambda: os.environ.get('FRONTEND_PORT', '7322'))
    static_frontend_files_path: str = Field(default_factory=lambda:
        os.environ.get(
            'STATIC_FRONTEND_FILES_PATH',
            app_data_dir_path('frontend', 'out'),
            # 'frontend/out'
        )
    )


class Webserver(BaseModel):
    bind_protocol: str = Field(default_factory=lambda: os.environ.get('BIND_PROTOCOL', 'http'))
    backend_port: str = Field(default_factory=lambda: os.environ.get('BACKEND_PORT', '7321'))
    bind_host: str = Field(default_factory=lambda: os.environ.get('BIND_HOST', 'localhost'))


class Environment(BaseModel):
    production: bool = Field(default_factory=lambda: os.environ.get('PRODUCTION', '1')=='1')
    backend: Backend = Backend()
    frontend: Frontend = Frontend()
    webserver: Webserver = Webserver()
    platform: Platform = Platform.get_platform()
    sqlite_file_path: str = os.path.join(platform.data_dir, 'db.sqlite3')
    sqlite_db_url: str = f'sqlite:///{sqlite_file_path}'

    def __init__(self, **data):
        super().__init__(**data)
        self.frontend.static_frontend = self.production


environment = Environment()
