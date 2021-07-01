from typing import Any, List, TypeVar, Callable, Type, cast


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


class Response:
    status: str
    code: int
    message: str

    def __init__(self, status: str, code: int, message: str) -> None:
        self.status = status
        self.code = code
        self.message = message

    @staticmethod
    def from_dict(obj: Any) -> "Response":
        assert isinstance(obj, dict)
        status = from_str(obj.get("status"))
        code = int(from_str(obj.get("code")))
        message = from_str(obj.get("message"))
        return Response(status, code, message)

    def to_dict(self) -> dict:
        result: dict = {}
        result["status"] = from_str(self.status)
        result["code"] = from_str(str(self.code))
        result["message"] = from_str(self.message)
        return result


class Language:
    name: str
    code: str
    translations: int
    percentage: float
    updated: str

    def __init__(
        self, name: str, code: str, translations: int, percentage: float, updated: str
    ) -> None:
        self.name = name
        self.code = code
        self.translations = translations
        self.percentage = percentage
        self.updated = updated

    @staticmethod
    def from_dict(obj: Any) -> "Language":
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        code = from_str(obj.get("code"))
        translations = from_int(obj.get("translations"))
        percentage = from_float(obj.get("percentage"))
        updated = from_str(obj.get("updated"))
        return Language(name, code, translations, percentage, updated)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_str(self.name)
        result["code"] = from_str(self.code)
        result["translations"] = from_int(self.translations)
        result["percentage"] = to_float(self.percentage)
        result["updated"] = from_str(self.updated)
        return result


class Result:
    languages: List[Language]

    def __init__(self, languages: List[Language]) -> None:
        self.languages = languages

    @staticmethod
    def from_dict(obj: Any) -> "Result":
        assert isinstance(obj, dict)
        languages = from_list(Language.from_dict, obj.get("languages"))
        return Result(languages)

    def to_dict(self) -> dict:
        result: dict = {}
        result["languages"] = from_list(lambda x: to_class(Language, x), self.languages)
        return result


class Languages:
    response: Response
    result: Result

    def __init__(self, response: Response, result: Result) -> None:
        self.response = response
        self.result = result

    @staticmethod
    def from_dict(obj: Any) -> "Languages":
        assert isinstance(obj, dict)
        response = Response.from_dict(obj.get("response"))
        result = Result.from_dict(obj.get("result"))
        return Languages(response, result)

    def to_dict(self) -> dict:
        result: dict = {}
        result["response"] = to_class(Response, self.response)
        result["result"] = to_class(Result, self.result)
        return result


def languages_from_dict(s: Any) -> Languages:
    return Languages.from_dict(s)


def languages_to_dict(x: Languages) -> Any:
    return to_class(Languages, x)
