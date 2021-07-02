from database.models.common.user_chat_message import UserChatMessage
from database.repository.user_repository import UserRepository
from aiogram import Bot, types
from utils.security import is_need_to_pass_captcha
from datetime import datetime, timedelta
from config import (
    CaptchaType,
    MessageType,
    RESTRICT_ALL,
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
            user_chats = await user_repo.get_chat_messages(member.id, False)

            if any(
                [
                    is_need_to_pass_captcha(user_secret_data),
                    message.chat.id not in [i.ChatId for i in user_chats],
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

                new_user_chats = [
                    UserChatMessage(
                        user_id=member.id,
                        chat_id=message.chat.id,
                        message_id=hey_msg.message_id,
                        message_type=MessageType.Welcome.value,
                        captcha_type=CaptchaType.Re.value,
                    ),
                    UserChatMessage(
                        user_id=member.id,
                        chat_id=message.chat.id,
                        message_id=game_msg.message_id,
                        message_type=MessageType.Captcha.value,
                        captcha_type=CaptchaType.Re.value,
                    ),
                ]

                await user_repo.add_chat_captcha(new_user_chats)

    else:
        gather(
            *[
                bot.send_message(
                    i.user.id, f"Я не администратор в этом чате: {message.chat.id}"
                )
                for i in chat_admins
            ]
        )
