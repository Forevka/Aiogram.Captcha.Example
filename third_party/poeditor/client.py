import aiohttp
from yarl import URL
from typing import Optional, Type
from types import TracebackType
from third_party.poeditor.models.languages import Languages, languages_from_dict
from third_party.poeditor.models.language_file_url import (
    LanguageFileURL,
    language_file_url_from_dict,
)

API_VERSION = 2


class PoeditorClient:
    def __init__(
        self,
        token: str,
        project_id: int,
        base_url: URL = URL("https://api.poeditor.com/"),
    ) -> None:
        self._base_url = base_url
        self._client = aiohttp.ClientSession(raise_for_status=True)

        self.project_id = project_id
        self.token = token

    async def close(self) -> None:
        return await self._client.close()

    async def __aenter__(self) -> "PoeditorClient":
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

    async def get_available_languages(
        self,
    ) -> Optional[Languages]:
        async with self._client.post(
            self._make_url(f"v{API_VERSION}/languages/list"),
            data={
                "api_token": self.token,
                "id": self.project_id,
            },
            raise_for_status=False,
        ) as resp:
            if resp.status == 200:
                ret = await resp.json()
                return languages_from_dict(ret)
            return None

    async def get_language_file_url(self, lang_id: str) -> Optional[LanguageFileURL]:
        async with self._client.post(
            self._make_url(f"v{API_VERSION}/projects/export"),
            data={
                "api_token": self.token,
                "id": self.project_id,
                "language": lang_id,
                "type": "key_value_json",
            },
            raise_for_status=False,
        ) as resp:
            if resp.status == 200:
                ret = await resp.json()
                return language_file_url_from_dict(ret)
            return None

    async def download_translation_file(self, url: str) -> Optional[bytes]:
        async with self._client.get(url, raise_for_status=False) as resp:
            if resp.status == 200:
                return await resp.read()
            return None
