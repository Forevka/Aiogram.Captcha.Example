from dataclasses import dataclass


@dataclass
class Lang:
	LangId: int
	Code: str

	__select__ = """ select "LangId", "Code" from "Lang" """

