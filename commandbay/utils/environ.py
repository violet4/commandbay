import sys
import os
from os.path import dirname
import platform as sys_platform
import pathlib
import sys

from pydantic import BaseModel, Field


if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    _in_bundle = True
else:
    _in_bundle = False


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


base_app_data_dir_path = dirname(dirname(dirname(os.path.abspath(__file__))))
def app_data_dir_path(*relative_path):
    return os.path.join(base_app_data_dir_path, *relative_path)


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
            app_data_dir_path('frontend', *([] if _in_bundle else ['out'])),
            # 'frontend/out'
        )
    )


class Webserver(BaseModel):
    bind_protocol: str = Field(default_factory=lambda: os.environ.get('BIND_PROTOCOL', 'http'))
    backend_port: str = Field(default_factory=lambda: os.environ.get('BACKEND_PORT', '7321'))
    bind_host: str = Field(default_factory=lambda: os.environ.get('BIND_HOST', 'localhost'))


_commandbay_base_dir: str = dirname(dirname(dirname(os.path.abspath(__file__))))
_app_data_directory: str = getattr(sys, '_MEIPASS', _commandbay_base_dir)
_static_dir: str = os.path.join(_app_data_directory, 'static')


class AppData(BaseModel):
    commandbay_base_dir: str = Field(default_factory=lambda: _commandbay_base_dir)
    app_data_directory: str = Field(default_factory=lambda: _app_data_directory)
    static_dir: str = Field(default_factory=lambda: _static_dir)


class Environment(BaseModel):
    production: bool = Field(default_factory=lambda: os.environ.get('PRODUCTION', '1')=='1')
    backend: Backend = Backend()
    frontend: Frontend = Frontend()
    webserver: Webserver = Webserver()
    platform: Platform = Platform.get_platform()
    sqlite_file_path: str = os.path.join(platform.data_dir, 'db.sqlite3')
    sqlite_db_url: str = f'sqlite:///{sqlite_file_path}'
    appData: AppData = AppData()
    in_bundle: bool = _in_bundle

    def __init__(self, **data):
        super().__init__(**data)
        self.frontend.static_frontend = self.production

    def user_data_dir_path(self, *relative_path):
        return os.path.join(self.platform.data_dir, *relative_path)

    @staticmethod
    def pyinstaller_app_data_dir_path(*relative_path):
        return os.path.join(_app_data_directory, *relative_path)

    @staticmethod
    def app_data_dir_path(*args):
        return app_data_dir_path(*args)


environment = Environment()
