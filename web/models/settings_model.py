from pydantic import BaseModel

class SettingsModel(BaseModel):
    user_id: int
    public_key: str
    chat_id: int
    welcome_message: str
    captcha_type: int
    is_need_to_delete_service_message: bool
