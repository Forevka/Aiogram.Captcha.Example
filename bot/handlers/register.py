from bot.handlers.callback.game_captcha import callback_game_captcha
from bot.handlers.commands.captcha import cmd_captcha
from bot.handlers.commands.start import cmd_start
from bot.handlers.messages.new_chat_members import new_chat_member
from aiogram import Dispatcher, Router, F
from typing import Union


def register_all(dp: Union[Dispatcher, Router]):
    dp.message.register(
        cmd_start,
        commands={
            "start",
            "help",
        },
    )

    dp.message.register(
        cmd_captcha,
        commands={
            "captcha",
        },
    )

    dp.message.register(new_chat_member, F.content_type == "new_chat_members")

    dp.callback_query.register(callback_game_captcha, F.game_short_name == "captcha")
