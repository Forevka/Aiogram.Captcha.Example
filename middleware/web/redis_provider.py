from config import REDIS_HOST
from typing import Awaitable, Callable

from aiogram.contrib.fsm_storage.redis import RedisStorage2
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class RedisProviderMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        super().__init__(app)
        self.storage = RedisStorage2(host=REDIS_HOST, db=8, prefix='captcha_service',)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request.state.storage = self.storage
        response = await call_next(request)
        
        return response