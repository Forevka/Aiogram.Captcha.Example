from typing import Awaitable, Callable
from aiogram import Bot

from config import TOKEN
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class BotProviderMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        super().__init__(app)
        self.bot = Bot(TOKEN)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request.state.bot = self.bot
        response = await call_next(request)

        return response