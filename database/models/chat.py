from dataclasses import dataclass
from typing import Optional


@dataclass
class Chat:
    ChatId: int
    Username: Optional[str]

    __select__ = """ select "ChatId", "Username" from "Chat" """
