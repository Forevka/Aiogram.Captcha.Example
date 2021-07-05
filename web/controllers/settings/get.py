from asyncio.tasks import gather
from functools import partial
from web.utils.cleanup_chat_after_validation import cleanup_chat_after_validation, suppres_coroutine
from utils.security import generate_user_secret, verify_hash
from fastapi import Depends, Request
from starlette.responses import JSONResponse, Response

from web.dependency_resolvers.aiogram_fsm_context_to_fastapi import UserRepoResolver
from web.dependency_resolvers.aiogram_bot_to_fastapi import AiogramBot
from web.templates import templates
from aiogram.utils.exceptions.base import TelegramAPIError
from contextlib import suppress
from config import AVAILABLE_CAPTCHA_NAME, MessageType

async def get_settings_page(
    request: Request,
    chat_id: int,
    user_id: int,
    public_key: str,
    storage: UserRepoResolver = Depends(UserRepoResolver),
    bot: AiogramBot = Depends(AiogramBot),
) -> Response:
    chat = await storage.chat_setting_repo.get(chat_id)
    if (chat is None):
        return templates.TemplateResponse(
            "wrong_origin.html",
            {
                "request": request,
            }
        )
    
    user = await storage.user_repo.get(user_id)
    if (user is None):
        return templates.TemplateResponse(
            "wrong_origin.html",
            {
                "request": request,
            }
        )
    
    user_secret_data = await storage.user_repo.get_security(user_id)

    if not user_secret_data or not all(
        [
            user_secret_data,
            verify_hash(
                user_secret_data.PrivateKey,
                public_key,
                user_secret_data.PublicKey,
            ),
        ],
    ):
        return templates.TemplateResponse(
            "wrong_origin.html",
            {
                "request": request,
            }
        )

    admins = []
    with suppress(TelegramAPIError):
        admins = await bot.bot.get_chat_administrators(chat_id,)


    is_admin = any([i for i in admins if i.user.id == bot.bot.id and i.is_chat_admin])
    if is_admin:
        chat_setting = await storage.chat_setting_repo.get(chat.ChatId)

        if chat_setting:
            chat = await bot.bot.get_chat(chat.ChatId)
            new_user_secret_data = generate_user_secret()

            await storage.user_repo.update_security(user_id, new_user_secret_data['public_key'], new_user_secret_data['private_key'], None)

            chat_msgs = await storage.user_repo.get_chat_messages(user_id, False, [MessageType.Settings.value, MessageType.ToPrivate.value,])

            gather(
                *map(
                    partial(suppres_coroutine, errors=[TelegramAPIError]),
                    [
                        bot.bot.delete_message(msg.ChatId, msg.MessageId)
                        for msg in chat_msgs
                    ],
                )
            )
            await storage.user_repo.cleanup_concrete_messages(user_id, [i.MessageId for i in chat_msgs])

            return templates.TemplateResponse(
                "settings.html",
                {
                    "request": request,
                    "chat_name": chat.title,
                    "welcome_message": chat_setting.WelcomeMessage,
                    "captcha_types": AVAILABLE_CAPTCHA_NAME,
                    "selected_captcha": chat_setting.CaptchaType,
                    "is_enabled": chat_setting.IsEnabled,
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "user_public_key": new_user_secret_data['public_key'],
                },
            )
    
    return templates.TemplateResponse(
        "wrong_origin.html",
        {
            "request": request,
        }
    )

