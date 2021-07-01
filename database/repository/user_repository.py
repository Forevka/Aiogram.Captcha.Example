from database.models.user import User
from asyncpg.connection import Connection


class UserRepository:
    def __init__(self, conn: Connection):
        self.conn = conn

    async def get(self, user_id: int):
        user = await self.conn.fetchrow(
            f"""{User.__select__} where "Id" = $1""", user_id
        )
        if user:
            return User(**user)

    async def create(self, user_id: int, lang_id: int):
        sql = """
        insert into "User" ("Id", "LangId") 
        values($1, $2) 
        on conflict do nothing 
        returning "Id", "LangId" 
        """
        res = await self.conn.fetchrow(
            sql,
            user_id,
            lang_id,
        )
        if res:
            return User(**res)
