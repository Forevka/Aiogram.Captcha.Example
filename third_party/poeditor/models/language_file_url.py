from dataclasses import dataclass
from typing import Any, TypeVar, Type, cast


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class Response:
    status: str
    code: int
    message: str

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


@dataclass
class Result:
    url: str

    @staticmethod
    def from_dict(obj: Any) -> "Result":
        assert isinstance(obj, dict)
        url = from_str(obj.get("url"))
        return Result(url)

    def to_dict(self) -> dict:
        result: dict = {}
        result["url"] = from_str(self.url)
        return result


@dataclass
class LanguageFileURL:
    response: Response
    result: Result

    @staticmethod
    def from_dict(obj: Any) -> "LanguageFileURL":
        assert isinstance(obj, dict)
        response = Response.from_dict(obj.get("response"))
        result = Result.from_dict(obj.get("result"))
        return LanguageFileURL(response, result)

    def to_dict(self) -> dict:
        result: dict = {}
        result["response"] = to_class(Response, self.response)
        result["result"] = to_class(Result, self.result)
        return result


def language_file_url_from_dict(s: Any) -> LanguageFileURL:
    return LanguageFileURL.from_dict(s)


def language_file_url_to_dict(x: LanguageFileURL) -> Any:
    return to_class(LanguageFileURL, x)
