import logging
from datetime import datetime, timedelta
from urllib.parse import quote

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from config import CAPTCHA_ROUTE, HOST, PROXY_PREFIX, TOKEN
from middleware.bot.redis_provider import RedisProviderMiddleware
from utils import generate_user_secret

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)

dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())
dp.middleware.setup(RedisProviderMiddleware())


@dp.message_handler(commands=['start', 'captcha', ])
async def cmd_start(message: types.Message):
    await message.bot.send_game(message.chat.id, 'captcha',)


@dp.callback_query_handler()
async def callback_vote_action(query: types.CallbackQuery, storage: RedisStorage2):
    user_secret_data = await storage.get_data(chat=query.from_user.id, user=query.from_user.id,)

    if (user_secret_data.get('passed_time', 0) == 0 or datetime.utcnow() > (datetime.fromtimestamp(user_secret_data.get('passed_time')) + timedelta(minutes=1))):
        user_secrets = generate_user_secret()
    else:
        user_secrets = user_secret_data

    await storage.set_data(chat=query.from_user.id, user=query.from_user.id, data=user_secrets,)

    await query.answer(url=f"{HOST}{PROXY_PREFIX}{CAPTCHA_ROUTE}?user_id={query.from_user.id}&first_name={quote(query.from_user.first_name)}",)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
