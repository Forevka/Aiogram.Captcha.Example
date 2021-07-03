from bot.middleware.i18n_provider import i18n_provider
from bot.middleware.user_provider import user_provider
from utils.translations import load_translations_from_file
from bot.middleware.database_provider import database_connection_provider
from aiogram import Bot, Dispatcher
from aiogram.dispatcher.router import Router
from config import (
    CONNECTION_STRING,
    TOKEN,
)

from bot.handlers.register import register_all
import asyncpg


async def initialize_startup(
    context: dict,
):
    context["db_pool"] = await asyncpg.create_pool(dsn=context["connection_string"])

    trans = await load_translations_from_file()
    #if not is_debug():
    #    trans = await pull_translations(POEDITOR_ID, POEDITOR_TOKEN)

    context["translations"] = trans


def run_polling():
    dp: Router = Dispatcher()

    dp.update.middleware(
        database_connection_provider,
    )

    dp.update.middleware(
        user_provider,
    )

    dp.update.middleware(
        i18n_provider,
    )

    dp.startup.register(initialize_startup)

    register_all(dp)

    bot = Bot(token=TOKEN)

    dp.run_polling(
        bot,
        context={
            "connection_string": CONNECTION_STRING,
        },
    )
