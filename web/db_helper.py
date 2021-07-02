from config import CONNECTION_STRING
import asyncpg


class DatabasePoolHelper:
    pool: asyncpg.Pool

    def __init__(
        self,
    ):
        self.is_pool_created = False

    async def create_pool(self):
        self.pool = await asyncpg.create_pool(dsn=CONNECTION_STRING)
        self.is_pool_created = True
