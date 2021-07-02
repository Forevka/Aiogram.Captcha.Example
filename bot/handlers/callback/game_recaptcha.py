from aiogram import Bot, types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from config import RECAPTCHA_ROUTE
from utils.security import (
    generate_game_url,
    generate_user_secret,
    is_need_to_pass_captcha,
)


async def callback_game_recaptcha(
    query: types.CallbackQuery,
    captcha_storage: RedisStorage,
    captcha_state: FSMContext,
    bot: Bot,
):
    user = query.from_user

    if query.message and query.message.reply_to_message:
        if user.id != query.message.reply_to_message.from_user.id:
            return await query.answer(
                "This is not for you.",
                show_alert=False,
            )

        user = query.message.reply_to_message.from_user

    user_data = await captcha_state.get_data()
    user_secret_data = user_data.get("secret", {})

    if is_need_to_pass_captcha(user_secret_data):
        user_secret_data = generate_user_secret()
        user_data["secret"] = user_secret_data

        await captcha_state.set_data(user_data)

        await query.answer(
            url=generate_game_url(
                RECAPTCHA_ROUTE,
                user.id,
                user.first_name,
                user_secret_data["public_key"],
            ),
        )
    else:
        await query.answer("Keep calm, you are not a bot")
