# https://github.com/claws/aioprometheus/blob/4786678b413d166c0b6e0041558d11bc1a7097b2/examples/frameworks/fastapi-example.py
import time
from typing import List

from starlette.datastructures import State
from starlette.middleware.base import BaseHTTPMiddleware
from aioprometheus.renderer import render
from aioprometheus.collectors import Summary, Counter, REGISTRY
from prometheus_client.utils import INF
from fastapi.responses import PlainTextResponse
from fastapi import APIRouter, FastAPI, Header, Request, Response


REQUESTS = Counter(
    'requests_total',
    'Total HTTP requests',
)
RESPONSE_LATENCY = Summary(
    'response_latency',
    'Number of seconds to respond to a request',
)


class CBState(State):
    requests_counter: Counter
    response_latency_summary: Summary


class CBFastAPI(FastAPI):
    state: CBState


class CBRequest(Request):
    app: CBFastAPI


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request:CBRequest, call_next):
        labels = {'path': '/'+str(request.url).split('/', maxsplit=3)[-1].split('?', maxsplit=1)[0]}

        requests_counter: Counter = request.app.state.requests_counter
        requests_counter.inc(labels)

        start = time.time()
        response = await call_next(request)
        seconds = time.time() - start

        response_latency_summary: Summary = request.app.state.response_latency_summary
        response_latency_summary.observe(labels, seconds)

        return response


prometheus_router = APIRouter()

@prometheus_router.get("", response_class=PlainTextResponse)
async def metrics(request: Request, accept: List[str]=Header(None)) -> Response:
    content, http_headers = render(REGISTRY, accept)
    return Response(content=content, media_type=http_headers['Content-Type'])


def initialize(app:CBFastAPI, api_router:APIRouter):
    app.add_middleware(PrometheusMiddleware)
    api_router.include_router(prefix="/metrics", router=prometheus_router)

    app.state.requests_counter = REQUESTS
    app.state.response_latency_summary = RESPONSE_LATENCY
