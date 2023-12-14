from html import unescape
import json
from aiohttp import ClientConnectorError, ClientSession
import os
import sys

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from commandbay.utils.environ import environment as env


async def log_request_body(request: Request):
    body = await request.body()
    body_text = body.decode()
    body_dict = json.loads(body_text)
    return body_dict


class SuccessResponseModel(BaseModel):
    success: bool


class ErrorResponseModel(BaseModel):
    error: str
    detail: str


class HtmlBaseModel(BaseModel):
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            if isinstance(v, str):
                kwargs[k] = unescape(v)
        super().__init__(*args, **kwargs)


def host_live_frontend_and_docs(app:FastAPI):
    docs_build_html = os.path.join('docs', 'build', 'html')
    print(f"Mounting /docs to docs_build_html '{docs_build_html}' '{os.path.abspath(docs_build_html)}'", file=sys.stderr)
    app.mount("/docs", StaticFiles(directory=docs_build_html), name="docs")

    @app.get('/{path:path}')
    async def proxy_frontend(path: str):
        async with ClientSession() as sess:
            ws = env.webserver
            fe = env.frontend
            frontend_dev_server = f'{ws.bind_protocol}://{ws.bind_host}:{fe.frontend_port}'
            full_path = f'{frontend_dev_server}/{path}'
            try:
                async with sess.get(full_path) as resp:
                    return HTMLResponse(
                        await resp.read(),
                        status_code=resp.status,
                        media_type=resp.content_type,
                    )
            except ClientConnectorError:
                raise HTTPException(404, "Can't connect to backend; is it running? npm run dev")


def host_static_frontend(app:FastAPI):
    @app.get("/{path:path}")
    async def catch_all(path: str, request: Request):
        print(f"path '{path}'", file=sys.stderr)
        # path "users"
        file_path = os.path.join(env.frontend.static_frontend_files_path, path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        file_path = os.path.join(env.frontend.static_frontend_files_path, f'{path}.html')
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        file_path = os.path.join(env.frontend.static_frontend_files_path, 'index.html')
        return FileResponse(file_path)

    print(f"Mounting / to '{env.frontend.static_frontend_files_path}' '{os.path.abspath(env.frontend.static_frontend_files_path)}'", file=sys.stderr)
    app.mount("/", StaticFiles(directory=env.frontend.static_frontend_files_path), name="frontend")
