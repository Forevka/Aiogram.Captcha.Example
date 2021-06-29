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
        self.username = ''

    async def cached_link_to_bot(self,) -> str:
        if (not self.username):
            self.username = (await self.bot.get_me()).username

        return f'https://t.me/{self.username}'

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request.state.bot = self.bot
        request.state.bot_link = await self.cached_link_to_bot()
        response = await call_next(request)

        return response