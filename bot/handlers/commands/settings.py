from config import MessageType
from database.models.common.user_chat_message import UserChatMessage
from aiogram.client.bot import Bot
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from database.repository.user_repository import UserRepository
from aiogram import types
from aiogram.utils.exceptions.base import TelegramAPIError
from utils.security import (
    generate_settings_url,
    generate_user_secret,
)
from utils.cached_bot_data import cache


async def cmd_settings(
    message: types.Message,
    bot: Bot,
    user_repo: UserRepository,
):
    if message.chat.id == message.from_user.id:
        return await message.answer(
            text="Please add me to a group",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Choose group",
                            url=f"{await cache.cached_link_to_bot(bot)}?startgroup=qwe"
                        )
                    ]
                ]
            ),
        )


    try:
        await bot.send_chat_action(message.from_user.id, 'typing')
    except TelegramAPIError:
        await message.reply(
            text="Please open chat with bot and write /start to him",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="To bot",
                            url=await cache.cached_link_to_bot(bot),
                        )
                    ]
                ]
            ),
        )

    new_user_data = generate_user_secret()

    await user_repo.update_security(
        message.from_user.id,
        new_user_data["public_key"],
        new_user_data["private_key"],
        None,
    )

    msg = await bot.send_message(
        chat_id=message.from_user.id,
        text=f"Settings for chat {message.chat.title}\nOpen it with linked button\n\n<b>Notice: it would be deleted after opening for security reason</b>",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Settings",
                        url=generate_settings_url(
                            message.from_user.id,
                            message.chat.id,
                            new_user_data["public_key"],
                        ),
                    )
                ]
            ]
        ),
        parse_mode="HTML"
    )

    await user_repo.add_chat_captcha(
        [
            UserChatMessage(
                user_id=message.from_user.id,
                chat_id=message.from_user.id,
                message_id=msg.message_id,
                message_type=MessageType.Settings.value,
                captcha_type=0,
            ),
            UserChatMessage(
                user_id=message.from_user.id,
                chat_id=message.chat.id,
                message_id=message.message_id,
                message_type=MessageType.Settings.value,
                captcha_type=0,
            )
        ]
    )
