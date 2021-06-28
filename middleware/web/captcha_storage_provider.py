from typing import Awaitable, Callable, Optional

from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from aioredis import Redis
from config import REDIS_HOST
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class CaptchaStorageProviderMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        super().__init__(app)
        self.storage = RedisStorage(
            Redis(host=REDIS_HOST, db=8,),
            prefix='captcha_service',
        )

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request.state.storage = self.storage
        response = await call_next(request)

        return response