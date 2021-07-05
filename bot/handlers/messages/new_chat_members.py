from functools import partial
from typing import cast

from aiogram.utils.exceptions.base import TelegramAPIError
from web.utils.cleanup_chat_after_validation import (
    suppres_coroutine,
)
from database.models.chat_setting import ChatSetting
from database.repository.chat_repository import ChatRepository
from database.repository.chat_settings_repository import ChatSettingsRepository
from database.models.common.user_chat_message import UserChatMessage
from database.repository.user_repository import UserRepository
from aiogram import Bot, types
from utils.security import is_need_to_pass_captcha
from datetime import datetime, timedelta
from config import (
    MessageType,
    RESTRICT_ALL,
    CAPTCHA_ID_TO_NAME,
)
import html
from asyncio import gather


async def new_chat_member(
    message: types.Message,
    bot: Bot,
    user_repo: UserRepository,
):
    if message.new_chat_members is None:
        return

    chat_admins = await bot.get_chat_administrators(message.chat.id)
    if any(
        (i for i in chat_admins if all([i.user.id == bot.id, i.can_restrict_members]))
    ):
        for member in message.new_chat_members:
            user_secret_data = await user_repo.get_security(member.id)
            user_chats = await user_repo.get_chat_messages(
                member.id,
                False,
                [MessageType.Welcome.value, MessageType.Captcha.value],
            )

            if all(
                [
                    is_need_to_pass_captcha(user_secret_data),
                    message.chat.id not in [i.ChatId for i in user_chats],
                ]
            ):
                chat_settings_repo = ChatSettingsRepository(user_repo.conn)
                chat_settings = await chat_settings_repo.get(message.chat.id)
                if not chat_settings:
                    chat_repo = ChatRepository(user_repo.conn)
                    await chat_repo.create(message.chat.id, message.chat.username)
                    chat_settings = cast(
                        ChatSetting, await chat_settings_repo.get(message.chat.id)
                    )

                hey_msg = await message.answer(
                    chat_settings.WelcomeMessage.format(
                        username=f'<a href="tg://user?id={member.id}">{html.escape(member.first_name, quote=False)}</a>',
                    ),
                    parse_mode="HTML",
                )
                game_msg = await message.reply_game(
                    CAPTCHA_ID_TO_NAME.get(chat_settings.CaptchaType, "captcha"),
                )

                await bot.restrict_chat_member(
                    message.chat.id,
                    member.id,
                    RESTRICT_ALL,
                    until_date=datetime.utcnow() + timedelta(days=365),
                )

                messages_in_this_chat = [
                    msg for msg in user_chats if msg.ChatId == message.chat.id
                ]

                gather(
                    *map(
                        partial(suppres_coroutine, errors=[TelegramAPIError]),
                        [
                            bot.delete_message(message.chat.id, msg.MessageId)
                            for msg in messages_in_this_chat
                        ],
                    )
                )
                await user_repo.cleanup_messages(
                    member.id,
                )

                new_user_chats = [
                    UserChatMessage(
                        user_id=member.id,
                        chat_id=message.chat.id,
                        message_id=hey_msg.message_id,
                        message_type=MessageType.Welcome.value,
                        captcha_type=chat_settings.CaptchaType,
                    ),
                    UserChatMessage(
                        user_id=member.id,
                        chat_id=message.chat.id,
                        message_id=game_msg.message_id,
                        message_type=MessageType.Captcha.value,
                        captcha_type=chat_settings.CaptchaType,
                    ),
                ]

                await user_repo.add_chat_captcha(new_user_chats)

    else:
        gather(
            *[
                bot.send_message(
                    i.user.id,
                    f"Please promote me to administrator in this chat: {message.chat.id}",
                )
                for i in chat_admins
            ]
        )
