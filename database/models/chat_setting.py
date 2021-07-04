import datetime
from dataclasses import dataclass


@dataclass
class ChatSetting:
	ChatId: int
	WelcomeMessage: str
	CaptchaType: int
	CreatedDateTime: datetime.datetime
	ModifiedBy: int
	ModifiedDateTime: datetime.datetime

	__select__ = """ select "ChatId", "CaptchaType", "CreatedDateTime", "WelcomeMessage", "ModifiedBy", "ModifiedDateTime" from "ChatSetting" """

