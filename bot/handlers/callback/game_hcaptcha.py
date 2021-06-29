from datetime import datetime, timedelta
from urllib.parse import quote

from aiogram import Bot, types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from config import HCAPTCHA_ROUTE, HOST, INVALIDATE_STATE_MINUTES, PROXY_PREFIX
from utils.security import generate_user_secret


async def callback_game_hcaptcha(query: types.CallbackQuery, captcha_storage: RedisStorage, captcha_state: FSMContext, bot: Bot):
    user = query.from_user

    if (query.message and query.message.reply_to_message):
        if (user.id != query.message.reply_to_message.from_user.id):
            return await query.answer('This is not for you.', show_alert=False,)

        user = query.message.reply_to_message.from_user

    user_data = await captcha_storage.get_data(bot, user.id, user.id,)

    user_secret_data = user_data.get('secret', {})

    if (user_secret_data.get('passed_time', 0) == 0 or datetime.utcnow() > (datetime.fromtimestamp(user_secret_data.get('passed_time', 0)) + timedelta(minutes=INVALIDATE_STATE_MINUTES))):
        user_data['secret'] = generate_user_secret()

    await captcha_storage.set_data(bot, user.id, user.id, user_data,)

    await query.answer(url=f"{HOST}{PROXY_PREFIX}{HCAPTCHA_ROUTE}?user_id={user.id}&first_name={quote(user.first_name)}&public_key={user_data['secret']['public_key']}",)
