from utils.partialclass import partialclass
from config import ANGLE_ROUTE, HCAPTCHA_ROUTE, RECAPTCHA_ROUTE
from bot.handlers.callback.game_captcha import GameCaptcha
from bot.handlers.commands.hcaptcha import cmd_hcaptcha
from bot.handlers.commands.angle import cmd_angle
from bot.handlers.commands.recaptcha import cmd_recaptcha
from bot.handlers.commands.start import cmd_start
from bot.handlers.messages.new_chat_members import new_chat_member
from aiogram import Dispatcher, Router, F
from typing import Union
from functools import partial, partialmethod

def register_all(dp: Union[Dispatcher, Router]):
    dp.message.register(
        cmd_start,
        commands={
            "start",
            "help",
        },
    )

    dp.message.register(
        cmd_recaptcha,
        commands={
            "recaptcha",
        },
    )

    dp.message.register(
        cmd_angle,
        commands={
            "angle",
        },
    )

    dp.message.register(
        cmd_hcaptcha,
        commands={
            "hcaptcha",
        },
    )

    dp.message.register(new_chat_member, F.content_type == "new_chat_members")

    dp.callback_query.register(
        partialclass(GameCaptcha, captcha_route=RECAPTCHA_ROUTE), F.game_short_name == "captcha"
    )
    dp.callback_query.register(
        partialclass(GameCaptcha, captcha_route=ANGLE_ROUTE), F.game_short_name == "angle"
    )
    dp.callback_query.register(
        partialclass(GameCaptcha, captcha_route=HCAPTCHA_ROUTE), F.game_short_name == "hcaptcha"
    )
