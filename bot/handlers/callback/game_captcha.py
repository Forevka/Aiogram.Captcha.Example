from utils.partialclass import BaseHandlerContextWrapper
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from utils.security import (
    generate_game_url,
    generate_user_secret,
    is_need_to_pass_captcha,
)


class GameCaptcha(BaseHandlerContextWrapper[types.CallbackQuery]):
    async def unpack_handle(
        self,
        event: types.CallbackQuery,
        captcha_state: FSMContext,
        captcha_route: str,
    ):
        user = event.from_user

        if event.message and event.message.reply_to_message:
            if user.id != event.message.reply_to_message.from_user.id:
                return await event.answer(
                    "This is not for you.",
                    show_alert=False,
                )

            user = event.message.reply_to_message.from_user

        user_data = await captcha_state.get_data()
        user_secret_data = user_data.get("secret", {})

        if is_need_to_pass_captcha(user_secret_data):
            user_secret_data = generate_user_secret()
            user_data["secret"] = user_secret_data

            await captcha_state.set_data(user_data)

            await self.event.answer(
                url=generate_game_url(
                    captcha_route,
                    user.id,
                    user.first_name,
                    user_secret_data["public_key"],
                ),
            )
        else:
            await self.event.answer("Keep calm, you are not a bot")
