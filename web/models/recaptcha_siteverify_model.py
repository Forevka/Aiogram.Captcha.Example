from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RecaptchaSiteverifyModel(BaseModel):
    success: Optional[bool] = None
    challenge_ts: Optional[datetime] = None
    hostname: Optional[str] = None
