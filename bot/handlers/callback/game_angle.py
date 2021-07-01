from web.utils.validation_state import ValidationStateEnum
from web.utils.validate_user_state import validate_user_state

from aiogram import Bot, types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from config import ANGLE_ROUTE
from utils.security import generate_game_url


async def callback_game_angle(
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

    old_user_data = await captcha_state.get_data()

    old_user_public_key = old_user_data["secret"]["public_key"]

    result, user_data = await validate_user_state(
        captcha_state, old_user_public_key, old_user_data
    )

    if (result == ValidationStateEnum.NeedToPass):
        await query.answer(
            url=generate_game_url(
                ANGLE_ROUTE, user.id, user.first_name, user_data.user_public_key
            ),
        )
    else:
        await query.answer("Keep calm, you are not a bot")
