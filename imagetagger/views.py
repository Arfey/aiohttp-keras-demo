import asyncio
from typing import Dict
from concurrent.futures import ProcessPoolExecutor

import aiohttp_jinja2
import markdown2
from aiohttp import web

from .worker import predict
from .utils import Config
from .constants import PROJECT_DIR


class SiteHandler:

    def __init__(self, conf: Config, executor: ProcessPoolExecutor):
        self._conf = conf
        self._executor = executor
        self._loop = asyncio.get_event_loop()

    @aiohttp_jinja2.template('index.html')
    async def index(self, request: web.Request) -> Dict[str, str]:
        with open(PROJECT_DIR / 'README.md') as f:
            text = markdown2.markdown(f.read())

        return {'text': text}

    async def predict(self, request: web.Request) -> web.Response:
        raw_data = await request.read()
        executor = request.app['executor']
        r = self._loop.run_in_executor
        raw_data = await r(executor, predict, raw_data)
        return web.Response(body=raw_data)