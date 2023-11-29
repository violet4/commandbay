import logging
import asyncio

from aiohttp import ClientSession, ClientWebSocketResponse
from fastapi import APIRouter, WebSocket
from fastapi.responses import HTMLResponse

from twitch_bot.resources.user import user_router
from twitch_bot.resources.app import app
from twitch_bot.resources.arduino_power import arduino_router
from twitch_bot.resources.kanboard import kanboard_router
from twitch_bot.resources.log_message import log_router
from twitch_bot.resources.random_num import random_router
from twitch_bot.resources.spotify import spotify_router, initialize_spotify
from twitch_bot.resources.do_tts import initialize_tts, tts_router


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

@api_router.get("/")
async def hello_world():
    return 'this is a sample message from an http call'

app.include_router(prefix="/api", router=api_router)

@app.get('/{path:path}')
async def proxy_frontend(path: str):
    async with ClientSession() as sess:
        frontend_dev_server = 'http://localhost:3000'
        async with sess.get(f'{frontend_dev_server}/{path}') as resp:
            return HTMLResponse(
                await resp.text(),
                status_code=resp.status,
                media_type=resp.content_type,
            )


@app.websocket('/{path:path}')
async def websocket_proxy(websocket: WebSocket, path: str):
    await websocket.accept()
    async with ClientSession() as session:
        async with session.ws_connect(f'ws://localhost:3000/{path}') as ws:
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
