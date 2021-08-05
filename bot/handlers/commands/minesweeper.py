from aiogram import types, Bot


async def cmd_minesweeper(message: types.Message, bot: Bot):
    await bot.send_game(
        message.chat.id,
        "minesweeper",
    )
