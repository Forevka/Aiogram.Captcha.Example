from asyncio import gather
from functools import partial
from database.models.user_captcha_message import UserCaptchaMessage
from aiogram.utils.exceptions.base import TelegramAPIError

from aiogram import Bot
from config import UNRESTRICT_ALL
from contextlib import suppress
from typing import Awaitable, List


async def suppres_coroutine(task: Awaitable, *errors):
    with suppress(*errors):
        await task


async def cleanup_chat_after_validation(
    bot: Bot,
    user_id: int,
    chats: List[UserCaptchaMessage],
):
    tasks = []

    grouped_chats = set()

    for chat in chats:
        if chat.ChatId not in grouped_chats:
            grouped_chats.add(chat.ChatId)
            tasks.append(
                bot.restrict_chat_member(chat.ChatId, user_id, UNRESTRICT_ALL)
            )
        
        tasks.append(
            bot.delete_message(chat.ChatId, chat.MessageId)
        )


    tasks.append(
        bot.send_message(
            user_id,
            "Turing test succesfully passed",
        )
    )

    gather(*map(partial(suppres_coroutine, TelegramAPIError), tasks))
