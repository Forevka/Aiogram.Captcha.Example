import datetime
from dataclasses import dataclass


@dataclass
class ChatSetting:
	ChatId: int
	CaptchaType: int
	CreatedDateTime: datetime.datetime

	__select__ = """ select "ChatId", "CaptchaType", "CreatedDateTime" from "ChatSetting" """

