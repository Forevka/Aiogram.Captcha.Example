from asyncio import gather

from aiogram import Bot
from config import UNRESTRICT_ALL
from contextlib import suppress
from itertools import chain
from typing import Awaitable, Dict, List


async def suppres_coroutine(task: Awaitable, *errors):
    with suppress(*errors):
        await task


async def cleanup_chat_after_validation(
    bot: Bot,
    user_id: int,
    chats: Dict[str, List[int]],
):
    tasks = [
        [
            *[bot.delete_message(chat_id, msg_id) for msg_id in msg_ids],
            bot.restrict_chat_member(chat_id, user_id, UNRESTRICT_ALL),
        ]
        for chat_id, msg_ids in chats.items()
    ]
    flatten_tasks = list(chain(*tasks)) + [
        bot.send_message(
            user_id,
            "Turing test succesfully passed",
        )
    ]

    gather(*map(suppres_coroutine, flatten_tasks))
