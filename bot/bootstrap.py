from aiogram import Bot, Dispatcher
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from aiogram.dispatcher.router import Router
from aioredis import Redis
from config import REDIS_HOST, TOKEN
from bot.middleware.captcha_storage_provider import CaptchaStorageProviderMiddleware

from bot.handlers.register import register_all


def run_polling():
    dp: Router = Dispatcher()
    dp.update.middleware(
        CaptchaStorageProviderMiddleware(
            storage=RedisStorage(
                Redis(
                    host=REDIS_HOST,
                    db=8,
                ),
                prefix="captcha_service",
            )
        )
    )

    register_all(dp)

    bot = Bot(token=TOKEN)

    dp.run_polling(bot)
