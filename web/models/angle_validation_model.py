from pydantic import BaseModel

class AngleValidationModel(BaseModel):
    user_id: int
    public_key: str