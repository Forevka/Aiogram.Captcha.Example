from database.models.common.user_chat_message import UserChatMessage
from typing import List, Optional
from database.models.user_captcha_message import UserCaptchaMessage
from datetime import datetime
from database.models.user_security import UserSecurity
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

    async def get_security(self, user_id: int,):
        sec = await self.conn.fetchrow(
            f"""{UserSecurity.__select__} where "UserId" = $1""", user_id
        )
        if sec:
            return UserSecurity(**sec)

    async def update_security(
        self, user_id: int, public_key: str, private_key: str, passed_time: Optional[datetime],
    ):
        sql = """
        insert into "UserSecurity"("UserId", "PublicKey", "PrivateKey", "PassedDateTime")
        values ($1, $2, $3, $4)
        on conflict ("UserId")
        DO update set 
          "PublicKey" = EXCLUDED."PublicKey",
          "PrivateKey" = EXCLUDED."PrivateKey",
          "PassedDateTime" = EXCLUDED."PassedDateTime"
        RETURNING "UserId", "PublicKey", "PrivateKey", "PassedDateTime";
        """

        sec = await self.conn.fetchrow(
            sql,
            user_id,
            public_key,
            private_key,
            passed_time,
        )
        if sec:
            return UserSecurity(**sec)

    async def add_chat_captcha(self, messages: List[UserChatMessage]):
        sql = """
        insert into "UserCaptchaMessage" ("UserId", "ChatId", "MessageId", "IsDeleted", "CreatedDateTime", "MessageType", "CaptchaType")
        values ($1, $2, $3, false, CURRENT_TIMESTAMP, $4, $5)
        """

        await self.conn.executemany(sql, [list(i.dict().values()) for i in messages])

    async def get_chat_messages(self, user_id: int, is_deleted: bool):
        sql = f"""
        {UserCaptchaMessage.__select__} where "UserId" = $1 and "IsDeleted" = $2
        """
        msgs = await self.conn.fetch(
            sql, user_id, is_deleted
        )

        return [UserCaptchaMessage(**i) for i in msgs]

    async def cleanup_messages(self, user_id: int,):
        sql = """
        update "UserCaptchaMessage"
        set "IsDeleted" = true,
            "DeletedDateTime" = CURRENT_TIMESTAMP
        where "UserId" = $1
        """

        await self.conn.execute(sql, user_id,)
