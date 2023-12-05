import logging
import asyncio
import os
from functools import wraps

import requests

from aiohttp import ClientSession, ClientWebSocketResponse
from fastapi import FastAPI, APIRouter, WebSocket, applications
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi import docs

from commandbay.resources.user import user_router
from commandbay.resources.arduino_power import arduino_router
from commandbay.resources.kanboard import kanboard_router
from commandbay.resources.log_message import log_router
from commandbay.resources.random_num import random_router
from commandbay.resources.rewards import rewards_router
from commandbay.resources.spotify import spotify_router, initialize_spotify
from commandbay.resources.do_tts import initialize_tts, tts_router


logging.basicConfig(level=logging.DEBUG)

initialize_spotify()
initialize_tts()

api_router = APIRouter()
api_router.include_router(prefix="/arduino",  router=arduino_router)
api_router.include_router(prefix="/kanboard", router=kanboard_router)
api_router.include_router(prefix='/spotify',  router=spotify_router)
api_router.include_router(prefix="/users", router=user_router)
api_router.include_router(prefix="/tts", router=tts_router)
api_router.include_router(prefix="/random/random", router=random_router)
api_router.include_router(prefix="/log", router=log_router)
api_router.include_router(prefix="/rewards", router=rewards_router)

app = FastAPI(
    openapi_url="/api/v1/openapi.json",
    docs_url='/api/v1/docs',
    version='0.1.0',
)

#TODO:don't hard-code violet.com.crt
# @app.get("/static/violet.com.crt")
# def get_ca_cert():
#     with open("static/violet.com.crt", 'rb') as fr:
#         return HTMLResponse(
#             fr.read(), headers={'Content-Type': 'application/x-x509-ca-cert'},
#         )
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(prefix="/api", router=api_router)


def swagger_monkey_patch(get_swagger_ui_html):
    @wraps(get_swagger_ui_html)
    def wrapper(*args, **kwargs):
        """
        credits:
            https://github.com/Beipy
            https://github.com/tiangolo/fastapi/issues/4924#issuecomment-1132398796
        Wrap the function which is generating the HTML for the /docs endpoint and
        overwrite the default values for the swagger js and css.
        """
        import inspect
        default_args = inspect.getfullargspec(get_swagger_ui_html).kwonlydefaults
        if default_args is None:
            return get_swagger_ui_html(*args, **kwargs)

        url_names = ['swagger_js_url', 'swagger_css_url']
        url_replacements = {k: default_args[k] for k in url_names}

        fixed_kwargs = dict()
        for key, url in url_replacements.items():
            filename = os.path.basename(url)
            static_filename = os.path.join('static', filename)
            abs_static_filename = os.path.abspath(static_filename)
            if not os.path.exists(abs_static_filename):
                resp = requests.get(url)
                if resp.status_code == 200:
                    with open(abs_static_filename, 'wb') as fw:
                        fw.write(resp.content)
            fixed_kwargs[key] = f'/{static_filename}'

        return get_swagger_ui_html(*args, **kwargs, **fixed_kwargs)
    return wrapper


applications.get_swagger_ui_html = swagger_monkey_patch(docs.get_swagger_ui_html)  # type: ignore[reportPrivateImportUsage]


@app.get('/{path:path}')
async def proxy_frontend(path: str):
    async with ClientSession() as sess:
        frontend_dev_server = 'http://localhost:7322'
        full_path = f'{frontend_dev_server}/{path}'
        async with sess.get(full_path) as resp:
            return HTMLResponse(
                await resp.read(),
                status_code=resp.status,
                media_type=resp.content_type,
            )


@app.websocket('/{path:path}')
async def websocket_proxy(websocket: WebSocket, path: str):
    await websocket.accept()
    async with ClientSession() as session:
        async with session.ws_connect(f'ws://localhost:7322/{path}') as ws:
            # Run two tasks concurrently: 
            # One for receiving messages from the client and forwarding them to the server
            # Another for receiving messages from the server and forwarding them to the client
            consumer_task = asyncio.ensure_future(consumer_handler(websocket, ws))
            producer_task = asyncio.ensure_future(producer_handler(websocket, ws))
            done, pending = await asyncio.wait(
                [consumer_task, producer_task], 
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()

async def consumer_handler(client_ws: WebSocket, server_ws: ClientWebSocketResponse):
    async for message in client_ws.iter_text():
        await server_ws.send_str(message)

async def producer_handler(client_ws: WebSocket, server_ws: ClientWebSocketResponse):
    async for message in server_ws:
        await client_ws.send_text(message.data)
