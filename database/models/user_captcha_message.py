import datetime
import typing
from dataclasses import dataclass


@dataclass
class UserCaptchaMessage:
	UserId: int
	ChatId: int
	MessageId: int
	IsDeleted: bool
	DeletedDateTime: typing.Optional[datetime.datetime]
	CreatedDateTime: datetime.datetime
	MessageType: int
	CaptchaType: int

	__select__ = """ select "UserId", "ChatId", "MessageId", "IsDeleted", "DeletedDateTime", "CreatedDateTime", "MessageType", "CaptchaType" from "UserCaptchaMessage" """

