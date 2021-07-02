import typing
from dataclasses import dataclass


@dataclass
class Chat:
	ChatId: int
	Username: typing.Optional[str]

	__select__ = """ select "ChatId", "Username" from "Chat" """

