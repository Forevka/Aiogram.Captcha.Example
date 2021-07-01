from dataclasses import dataclass


@dataclass
class User:
    Id: int
    LangId: int

    __select__ = """ select "Id", "LangId" from "User" """
