from typing import Optional
from database.models.chat import Chat
from asyncpg.connection import Connection


class ChatRepository:
    def __init__(self, conn: Connection):
        self.conn = conn

    async def get(self, chat_id: int):
        user = await self.conn.fetchrow(
            f"""{Chat.__select__} where "ChatId" = $1""", chat_id
        )
        if user:
            return Chat(**user)

    async def create(self, chat_id: int, username: Optional[str]):
        sql = """
        insert into "Chat" ("ChatId", "Username") 
        values($1, $2) 
        on conflict do nothing 
        returning "ChatId", "Username" 
        """
        res = await self.conn.fetchrow(
            sql,
            chat_id,
            username,
        )
        if res:
            return Chat(**res)
