from pydantic import BaseModel


class RecaptchaValidationModel(BaseModel):
    token: str
    user_id: int
    public_key: str
