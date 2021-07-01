from web.models.recaptcha_siteverify_model import RecaptchaSiteverifyModel
import aiohttp
from yarl import URL
from typing import Optional, Type
from types import TracebackType


class CaptchaClient:
    def __init__(
        self,
        base_url: URL,
    ) -> None:
        self._base_url = base_url
        self._client = aiohttp.ClientSession(raise_for_status=True)

    async def close(self) -> None:
        return await self._client.close()

    async def __aenter__(self) -> "CaptchaClient":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> Optional[bool]:
        await self.close()
        return None

    def _make_url(self, path: str) -> URL:
        return self._base_url / path

    async def validate_token(
        self,
        token: str,
        secret: str,
    ) -> Optional[RecaptchaSiteverifyModel]:
        async with self._client.post(
            self._make_url("siteverify"),
            data={
                "secret": secret,
                "response": token,
            },
            raise_for_status=False,
        ) as resp:
            if resp.status == 200:
                return RecaptchaSiteverifyModel(**await resp.json())
            return None
