import sys
import logging
import asyncio
import os
from functools import wraps

import requests

from aiohttp import ClientSession, ClientWebSocketResponse
from fastapi import FastAPI, APIRouter, WebSocket, applications
from fastapi.staticfiles import StaticFiles
from fastapi.openapi import docs

from commandbay.resources.user import user_router
from commandbay.resources.arduino_power import arduino_router
from commandbay.resources.kanboard import kanboard_router
from commandbay.resources.log_message import log_router
from commandbay.resources.random_num import random_router
from commandbay.resources.rewards import rewards_router
from commandbay.resources.spotify import spotify_router
from commandbay.resources.do_tts import initialize_tts, tts_router
from commandbay.resources.utils import host_live_frontend_and_docs, host_static_frontend
from commandbay.resources.settings import settings_router
from commandbay.utils.environ import environment as env
import commandbay


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

initialize_tts()

api_router = APIRouter()
api_router.include_router(prefix="/arduino",  router=arduino_router)
api_router.include_router(prefix="/kanboard", router=kanboard_router)
api_router.include_router(prefix='/spotify',  router=spotify_router)
api_router.include_router(prefix="/users", router=user_router)
api_router.include_router(prefix="/tts", router=tts_router)
api_router.include_router(prefix="/random", router=random_router)
api_router.include_router(prefix="/log", router=log_router)
api_router.include_router(prefix="/rewards", router=rewards_router)
api_router.include_router(prefix="/settings", router=settings_router)


@api_router.get('/version')
def get_version():
    return {'version': commandbay.full_version}


app = FastAPI(
    openapi_url="/api/v0/openapi.json",
    docs_url='/api/v0/docs',
    version=commandbay.__version__,
    title="CommandBay",
)

#TODO:don't hard-code violet.com.crt
# @app.get("/static/violet.com.crt")
# def get_ca_cert():
#     with open("static/violet.com.crt", 'rb') as fr:
#         return HTMLResponse(
#             fr.read(), headers={'Content-Type': 'application/x-x509-ca-cert'},
#         )
# static_dir = "static" if os.path.exists('static') else os.path.join('..', 'static')

print(f"Mounting /static to '{env.backend.static_backend_files_path}' '{os.path.abspath(env.backend.static_backend_files_path)}", file=sys.stderr)
app.mount("/static", StaticFiles(directory=env.backend.static_backend_files_path), name="static")
app.include_router(prefix="/api", router=api_router)

# serve the now-static "compiled" frontend code built with `npm run build`
if env.production:
    host_static_frontend(app)
# serve the frontend development nextjs server from a `npm run dev` process
else:  # dev
    host_live_frontend_and_docs(app)


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
            # THIS AFFECTS THE URL THAT GETS PUT IN THE SWAGGER UI HTML
            # the urls need to stay relative, not absolute!
            static_url_path = f'static/{filename}'
            static_filename_abspath = (
                env.pyinstaller_app_data_dir_path
                if env.production
                else env.app_data_dir_path
            )('static', filename)
            if not os.path.exists(static_filename_abspath):
                resp = requests.get(url)
                if resp.status_code == 200:
                    with open(static_filename_abspath, 'wb') as fw:
                        fw.write(resp.content)
            fixed_kwargs[key] = f'/{static_url_path}'

        return get_swagger_ui_html(*args, **kwargs, **fixed_kwargs)
    return wrapper


applications.get_swagger_ui_html = swagger_monkey_patch(docs.get_swagger_ui_html)  # type: ignore[reportPrivateImportUsage]


@app.websocket('/{path:path}')
async def websocket_proxy(websocket: WebSocket, path: str):
    await websocket.accept()
    async with ClientSession() as session:
        async with session.ws_connect(f'ws://{env.webserver.bind_host}:{env.frontend.frontend_port}/{path}') as ws:
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
