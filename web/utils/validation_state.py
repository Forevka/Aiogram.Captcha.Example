from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from typing import Optional


class ValidationStateEnum(Enum):
    Passed = 1
    WrongOrigin = 2
    NeedToPass = 3

class ValidationResponseData(BaseModel):
    user_public_key: str
    passed_at: Optional[datetime]
    pass_again: Optional[datetime]
    current_utc_time: Optional[datetime]