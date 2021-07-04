from typing import Optional
from database.models.chat import Chat
from asyncpg.connection import Connection


class ChatRepository:
    def __init__(self, conn: Connection):
        self.conn = conn

    async def get(self, chat_id: int):
        chat = await self.conn.fetchrow(
            f"""{Chat.__select__} where "ChatId" = $1""", chat_id
        )
        if chat:
            return Chat(**chat)

    async def create(self, chat_id: int, username: Optional[str]):
        sql = """
	    select 
            "ChatId", 
            "Username" 
        from create_default_chat($1, $2)
        """
        res = await self.conn.fetchrow(
            sql,
            chat_id,
            username,
        )
        if res:
            return Chat(**res)
    
