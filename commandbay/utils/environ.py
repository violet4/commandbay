import os

from pydantic import BaseModel, Field


class Backend(BaseModel):
    pass


class Frontend(BaseModel):
    static_frontend: bool = False
    static_frontend_files_path: str = Field(default_factory=lambda: os.environ.get('STATIC_FRONTEND_FILES_PATH', 'frontend/out'))
    frontend_port: str = Field(default_factory=lambda: os.environ.get('FRONTEND_PORT', '7322'))


class Webserver(BaseModel):
    bind_protocol: str = Field(default_factory=lambda: os.environ.get('BIND_PROTOCOL', 'http'))
    backend_port: str = Field(default_factory=lambda: os.environ.get('BACKEND_PORT', '7321'))
    bind_host: str = Field(default_factory=lambda: os.environ.get('BIND_HOST', 'localhost'))


class Environment(BaseModel):
    production: bool = Field(default_factory=lambda: os.environ.get('PRODUCTION', '1')=='1')
    backend: Backend = Backend()
    frontend: Frontend = Frontend()
    webserver: Webserver = Webserver()

    def __init__(self, **data):
        super().__init__(**data)
        self.frontend.static_frontend = self.production


environment = Environment()
