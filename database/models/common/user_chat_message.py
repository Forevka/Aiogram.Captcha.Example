from pydantic import BaseModel


class UserChatMessage(BaseModel):
    user_id: int
    chat_id: int
    message_id: int
    message_type: int
    captcha_type: int
