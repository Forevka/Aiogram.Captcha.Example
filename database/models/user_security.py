import datetime
import typing
from dataclasses import dataclass


@dataclass
class UserSecurity:
	UserId: int
	PublicKey: typing.Any
	PrivateKey: typing.Any
	PassedDateTime: typing.Optional[datetime.datetime]

	__select__ = """ select "UserId", "PublicKey", "PrivateKey", "PassedDateTime" from "UserSecurity" """

