from database.repository.chat_repository import ChatRepository
from database.repository.user_repository import UserRepository
from typing import Any, Awaitable, Callable, Dict
from aiogram import types
from aiogram.types import Update

from config import Lang, DEFAULT_LANG, all_language_codes


async def user_provider(
    handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
    event: Update,
    data: Dict[str, Any],
) -> Any:
    from_user: types.User = data["event_from_user"]
    if (from_user):
        data["user_repo"] = UserRepository(data["db_conn"])

        user = await data["user_repo"].get(from_user.id)
        if (not user):
            lang_id = DEFAULT_LANG.value
            if from_user.language_code and from_user.language_code in all_language_codes:
                lang_id = Lang[from_user.language_code].value

            user = await data["user_repo"].create(
                from_user.id, lang_id
            )

        data["user"] = user

    from_chat: types.Chat = data["event_chat"]
    if (from_chat and "group" in from_chat.type):
        data["chat_repo"] = ChatRepository(data["db_conn"])

        chat = await data["chat_repo"].get(from_chat.id)
        if (not chat):
            chat = await data["chat_repo"].create(from_chat.id, from_chat.username)

        data["chat"] = chat
        

    await handler(event, data)
