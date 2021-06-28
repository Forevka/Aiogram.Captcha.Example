from typing import Any, Awaitable, Callable, Dict, cast

from aiogram import Bot
from aiogram.dispatcher.fsm.middleware import FSMContextMiddleware
from aiogram.types import Update


class CaptchaStorageProviderMiddleware(FSMContextMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        bot: Bot = cast(Bot, data["bot"])
        context = self.resolve_event_context(bot, data)
        data["captcha_storage"] = self.storage
        if context:
            data.update({"captcha_state": context, "raw_state": await context.get_state()})
            if self.isolate_events:
                async with self.storage.lock(
                    bot=bot, chat_id=context.chat_id, user_id=context.user_id
                ):
                    return await handler(event, data)
        return await handler(event, data)
