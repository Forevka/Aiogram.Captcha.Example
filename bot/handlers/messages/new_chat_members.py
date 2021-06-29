from aiogram import Bot, types
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from utils.security import is_need_to_pass_captcha
from datetime import datetime, timedelta
from config import (
    RESTRICT_ALL,
)
import html
from asyncio import gather


async def new_chat_member(
    message: types.Message, captcha_storage: RedisStorage, bot: Bot
):
    if message.new_chat_members is None:
        return

    chat_admins = await bot.get_chat_administrators(message.chat.id)
    if any(
        (i for i in chat_admins if all([i.user.id == bot.id, i.can_restrict_members]))
    ):
        for member in message.new_chat_members:
            user_data = await captcha_storage.get_data(bot, member.id, member.id)
            user_secret_data = user_data.get("secret", {})
            user_chats = user_data.get("chats", {})

            if any(
                [
                    is_need_to_pass_captcha(user_secret_data),
                    str(message.chat.id) not in user_chats,
                ]
            ):
                hey_msg = await message.answer(
                    f'Hey, <a href="tg://user?id={member.id}">{html.escape(member.first_name, quote=False)}</a> please pass the captcha!',
                    parse_mode="HTML",
                )
                game_msg = await message.reply_game(
                    "captcha",
                )
                await bot.restrict_chat_member(
                    message.chat.id,
                    member.id,
                    RESTRICT_ALL,
                    until_date=datetime.utcnow() + timedelta(days=365),
                )

                user_chats[message.chat.id] = [
                    hey_msg.message_id,
                    game_msg.message_id,
                ]

                user_data["chats"] = user_chats

                await captcha_storage.set_data(
                    bot,
                    member.id,
                    member.id,
                    user_data,
                )
    else:
        gather(
            *[
                bot.send_message(
                    i.user.id, f"Я не администратор в этом чате: {message.chat.id}"
                )
                for i in chat_admins
            ]
        )
