import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from urllib.parse import quote

from config import TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)

dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['start', 'captcha',])
async def cmd_start(message: types.Message):
    await message.bot.send_game(message.chat.id, 'captcha',)


@dp.callback_query_handler()
async def callback_vote_action(query: types.CallbackQuery):
    await query.answer(url=f"https://forevka-aiogram-captcha-example-rwqqrjqqhxvvw-80.githubpreview.dev/captcha?user_id={query.from_user.id}&first_name={quote(query.from_user.first_name)}",)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
