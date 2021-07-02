from typing import Awaitable, Callable
from web.db_helper import DatabasePoolHelper
from fastapi import Request, Response
from starlette.types import ASGIApp
from starlette.middleware.base import BaseHTTPMiddleware


class DatabaseProviderMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        super().__init__(app)
        self.db_helper = DatabasePoolHelper()

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if not self.db_helper.is_pool_created:
            await self.db_helper.create_pool()

        request.state.connection = await self.db_helper.pool.acquire()
        response = await call_next(request)
        if request.state.connection is not None:
            await self.db_helper.pool.release(request.state.connection)

        return response
