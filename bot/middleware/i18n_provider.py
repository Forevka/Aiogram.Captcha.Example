from utils.translation_holder import TranslationHolder
from config import DEFAULT_LANG, Lang
from typing import Any, Awaitable, Callable, Dict
from aiogram.types import Update


async def i18n_provider(
    handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
    event: Update,
    data: Dict[str, Any],
) -> Any:
    user = data.get("user")

    translations: dict = data['context']['translations']

    if user:
        data["_"] = TranslationHolder(translations, user.LangId,)
    else:
        data["_"] = TranslationHolder(translations, Lang(DEFAULT_LANG).value,)
        
    await handler(event, data)
