from database.models.chat_setting import ChatSetting
from asyncpg.connection import Connection


class ChatSettingsRepository:
    def __init__(self, conn: Connection):
        self.conn = conn

    async def get(self, chat_id: int):
        chat = await self.conn.fetchrow(
            f"""{ChatSetting.__select__} where "ChatId" = $1""", chat_id
        )
        if chat:
            return ChatSetting(**chat)

    async def update(
        self,
        chat_id: int,
        welcome_message: str,
        captcha_type: int,
        modified_by: int,
    ):
        sql = """
        update "ChatSetting"
        set "CaptchaType" = $1,
                "WelcomeMessage" = $2,
                "ModifiedBy" = $3,
                "ModifiedDateTime" = CURRENT_TIMESTAMP
        where "ChatId" = $4
        """
        await self.conn.execute(
            sql, captcha_type, welcome_message, modified_by, chat_id
        )
